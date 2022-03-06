#include <sstream>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <cmath>

using namespace std;

int main(int argc, char* argv[]) {
   string line; 
   int points=0;
   int z;
   double x, y, minimum, maximum;
   int mode = atoi(argv[1]);

   fstream infile;
   infile.open(argv[2],ios::in);
   while (getline(infile, line)) {
      stringstream linestream(line);
      linestream >> x >> y;
      if ( points == 0 ) 
      {
         minimum = y;
         maximum = y;
      } 
      else  
      {            
         if ( y <= minimum ) minimum = y;
         if ( y >= maximum ) maximum = y;
      }
      points++;
   }
   infile.close(); 
  
   switch(mode)
   {
      case 1:
      {
         double width = atof(argv[3]);
         double new_minimum = minimum - 0.5 * width;
         double new_maximum = maximum + 0.5 * width;
         int bin = ( new_maximum - new_minimum ) / width;
         int bins[bin];

   	 for (int i=0; i<bin; i++) {
      	    bins[i]=0;
   	 }

   	 infile.open(argv[2],ios::in);

   	 while (getline(infile, line)) {
      	    stringstream linestream(line);
      	    linestream >> x >> y;
            z = (y - new_minimum)/ width;
            bins[z]++;
         }
         infile.close();
 
         double coor;
         double norm;
 
         for ( int i=0; i < bin; i++ ) {
            coor = minimum + i * width;
      	    norm = bins[i]/(double)points;
            cout << coor << " " << norm << endl;
         }

      }
      break;
 
      case 2:
      {
         int bins = atoi(argv[3]);
         double width = (maximum - minimum)/(bins-1);
         int bin[bins];
         for (int i=0; i<bins; i++) {
            bin[i]=0;
         }
         infile.open(argv[2],ios::in);

         double new_minimum = minimum - 0.5 * width;

         while (getline(infile, line)) {
            stringstream linestream(line);
            linestream >> x >> y;
            z = (y - new_minimum)/ width;
            bin[z]++;
         }
         infile.close();
        
         double coor;
         double norm;

         for ( int i=0; i < bins; i++ ) {
            coor = minimum + i * width;
            norm = bin[i]/(double)points;
            cout << coor << " " << norm << endl;
         }
      }
      break;

      case 3:
      {
         int bins = atoi(argv[3]);
         double min = atoi(argv[4]);
         double max = atoi(argv[5]);

         double width = (max - min)/bins;
         int bin[bins];

         for (int i=0; i<bins; i++) {
            bin[i]=0;
         }

         infile.open(argv[2],ios::in);

         while (getline(infile, line)) {
            stringstream linestream(line);
            linestream >> x >> y;
            z = (y - min)/ width;
            bin[z]++;
         }
         infile.close();

         double coor;
         double norm;

         for ( int i=0; i < bins; i++ ) {
            coor = min + i * width;
            norm = bin[i]/(double)points;
            cout << coor << " " << norm << endl;
         }
      }
      break;
     
      default:
      {
         cout << "choose 1 or 2 or 3" << endl;
      }
      break;
   }

   return 0;	
}
