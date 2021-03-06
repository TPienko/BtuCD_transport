# REFERENCE
# 
# D. L. Mobley, A. P. Graves, J. D. Chodera, A. C. McReynolds, B. K. Shoichet and K. A. Dill, "Predicting absolute ligand binding free energies to a simple model site," Journal of Molecular Biology 371(4):1118-1134 (2007).
# http://dx.doi.org/10.1016/j.jmb.2007.06.002

from __future__ import print_function
import numpy # numerical array library
import pymbar # multistate Bennett acceptance ratio
from pymbar import timeseries # timeseries analysis
# Constants.
kB = 1.381e-23 * 6.022e23 / 1000.0 # Boltzmann constant in kJ/mol/K

temperature = 310.15 # assume a single temperature -- can be overridden with data from center.dat 
# Parameters
K = 33 # number of umbrellas
N_max = 500001 # maximum number of snapshots/simulation
T_k = numpy.ones(K,float)*temperature # inital temperatures are all equal 
beta = 1.0 / (kB * temperature) # inverse temperature of simulations (in 1/(kJ/mol))
chi_min = 25.625 # min for PMF
chi_max = 37.175 # max for PMF
nbins = 33 # number of bins for 1D PMF

# Allocate storage for simulation data
N_k = numpy.zeros([K], dtype = int) # N_k[k] is the number of snapshots from umbrella simulation k
K_k = numpy.zeros([K]) # K_k[k] is the spring constant (in kJ/mol/deg**2) for umbrella simulation k
chi0_k = numpy.zeros([K]) # chi0_k[k] is the spring center location (in deg) for umbrella simulation k
chi_kn = numpy.zeros([K,N_max]) # chi_kn[k,n] is the torsion angle (in deg) for snapshot n from umbrella simulation k
u_kn = numpy.zeros([K,N_max]) # u_kn[k,n] is the reduced potential energy without umbrella restraints of snapshot n of umbrella simulation k
g_k = numpy.zeros([K]);

# Read in umbrella spring constants and centers.
infile = open('centers.dat', 'r')
lines = infile.readlines()
infile.close()
for k in range(K):
    # Parse line k.
    line = lines[k]
    tokens = line.split()
    chi0_k[k] = float(tokens[0]) # spring center locatiomn (in deg)
    #K_k[k] = float(tokens[1]) * (numpy.pi/180)**2 # spring constant (read in kJ/mol/rad**2, converted to kJ/mol/deg**2)    
    K_k[k] = float(tokens[1]) # spring constant (read in kJ/mol/A**2)
if len(tokens) > 2:
        T_k[k] = float(tokens[2])  # temperature the kth simulation was run at.

beta_k = 1.0/(kB*T_k)   # beta factor for the different temperatures
DifferentTemperatures = True
if (min(T_k) == max(T_k)):
    DifferentTemperatures = False            # if all the temperatures are the same, then we don't have to read in energies.
# Read the simulation data
for k in range(K):
    # Read torsion angle data.
    filename = 'data/no_ATP/open_eq_HMR_%d.dat' % k
    print("Reading %s..." % filename)
    infile = open(filename, 'r')
    lines = infile.readlines()
    infile.close()
    # Parse data.
    n = 0
    for line in lines:
        if line[0] != '#' and line[0] != '@':
            tokens = line.split()
            chi = float(tokens[1]) # torsion angle
            # wrap chi_kn to be within [-180,+180)
            while(chi < -180.0):
                chi += 360.0
            while(chi >= +180.0):
                chi -= 360.0
            chi_kn[k,n] = chi
            
            n += 1
    N_k[k] = n

    if (DifferentTemperatures):  # if different temperatures are specified the metadata file, 
                                 # then we need the energies to compute the PMF
        # Read energies
        filename = 'data/prod%d_energies.xvg' % k
        print("Reading %s..." % filename)
        infile = open(filename, 'r')
        lines = infile.readlines()
        infile.close()
        # Parse data.
        n = 0
        for line in lines:
            if line[0] != '#' and line[0] != '@':
                tokens = line.split()            
                u_kn[k,n] = beta_k[k] * (float(tokens[2]) - float(tokens[1])) # reduced potential energy without umbrella restraint
                n += 1

    # Compute correlation times for potential energy and chi
    # timeseries.  If the temperatures differ, use energies to determine samples; otherwise, use the cosine of chi
            
    if (DifferentTemperatures):        
        g_k[k] = timeseries.statisticalInefficiency(u_kn[k,:], u_kn[k,0:N_k[k]])
        print("Correlation time for set %5d is %10.3f" % (k,g_k[k]))
        indices = timeseries.subsampleCorrelatedData(u_kn[k,0:N_k[k]])
    else:
        chi_radians = chi_kn[k,0:N_k[k]]/(180.0/numpy.pi)
        g_cos = timeseries.statisticalInefficiency(numpy.cos(chi_radians))
        g_sin = timeseries.statisticalInefficiency(numpy.sin(chi_radians))
        print("g_cos = %.1f | g_sin = %.1f" % (g_cos, g_sin))
        g_k[k] = max(g_cos, g_sin)
        print("Correlation time for set %5d is %10.3f" % (k,g_k[k]))
        indices = timeseries.subsampleCorrelatedData(chi_radians, g=g_k[k]) 
    # Subsample data.
    N_k[k] = len(indices)
    u_kn[k,0:N_k[k]] = u_kn[k,indices]
    chi_kn[k,0:N_k[k]] = chi_kn[k,indices]

N_max = numpy.max(N_k) # shorten the array size
u_kln = numpy.zeros([K,K,N_max], numpy.float64) # u_kln[k,l,n] is the reduced potential energy of snapshot n from umbrella simulation k evaluated at umbrella l

# Set zero of u_kn -- this is arbitrary.
u_kn -= u_kn.min()

# Construct torsion bins
print("Binning data...")
delta = (chi_max - chi_min) / float(nbins)
# compute bin centers
bin_center_i = numpy.zeros([nbins], numpy.float64)
for i in range(nbins):
    bin_center_i[i] = chi_min + delta/2 + delta * i
# Bin data
bin_kn = numpy.zeros([K,N_max], numpy.int32)
for k in range(K):
    for n in range(N_k[k]):
        # Compute bin assignment.
        bin_kn[k,n] = int((chi_kn[k,n] - chi_min) / delta)

# Evaluate reduced energies in all umbrellas
print("Evaluating reduced potential energies...")
for k in range(K):
    for n in range(N_k[k]):
        # Compute minimum-image torsion deviation from umbrella center l
        dchi = chi_kn[k,n] - chi0_k
        for l in range(K):
            if (abs(dchi[l]) > 180.0):
                dchi[l] = 360.0 - abs(dchi[l])

        # Compute energy of snapshot n from simulation k in umbrella potential l
        u_kln[k,:,n] = u_kn[k,n] + beta_k[k] * (K_k/2.0) * dchi**2

# Initialize MBAR.
print("Running MBAR...")
mbar = pymbar.MBAR(u_kln, N_k, verbose = True)

# Compute PMF in unbiased potential (in units of kT).
results = mbar.computePMF(u_kn, bin_kn, nbins, return_dict=True)
f_i = results['f_i']
df_i = results['df_i']

# Write out PMF
print("PMF (in units of kT)")
print("%8s %8s %8s" % ('bin', 'f', 'df'))
for i in range(nbins):
    print("%8.1f %8.3f %8.3f" % (bin_center_i[i], f_i[i], df_i[i]))
