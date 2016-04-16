//=========================================================================
// cordic_test.cpp
//=========================================================================
// @brief: A C++ test bench (TB) for validating the sine & cosine functions
//         implemented using CORDIC.
/* @desc: 
   1. This TB generates angles between [1, NUM_DEGREE).
   2. It calculates the difference (or errors) between the results from
      CORDIC-based sin/cos with those from standard math library in <math.h>.
   3. All results are logged in the file out.dat for debugging purposes.
   4. The final cumulative errors are printed.
*/

#include <math.h>
#include <hls_stream.h>
#include <iostream>
#include <fstream>

#include "cordic.h"

//--------------------------------------
// main function of TB
//--------------------------------------
int main(int argc, char** argv)
{
  // cordic output
  bit32_t sum = 0;
  
  // arrays to store the output
  int sum_array[25];
  
  // HLS streams for communicating with the cordic block
  hls::stream<bit32_t> cordic_in;
  hls::stream<bit32_t> cordic_out;

  //------------------------------------------------------------ 
  // Send data to CORDIC sim
  //------------------------------------------------------------ 
  for (int i = 0; i < 5; i++) {
    for ( int j = 0; j < 5; j++ ) {
		// Send both inputs to the HLS module
		bit32_t a;
		bit32_t b;
		a = i;
		b = j;
		cordic_in.write( a );
		cordic_in.write( b );
	}
  }

  //------------------------------------------------------------ 
  // Execute CORDIC sim and store results
  //------------------------------------------------------------ 
  for (int i = 0; i < 25; i++) {
    // Run the HLS function 
    dut( cordic_in, cordic_out );

    // Read the two 32-bit cosine output words, low word first
    sum = cordic_out.read();
    
    // Store to array
    sum_array[i] = sum;
  }

  //------------------------------------------------------------ 
  // Check results
  //------------------------------------------------------------ 
  int idx = 0;
  int act_sum[25];
  for (int i = 0; i < 5; i++) {
    for ( int j = 0; j < 5; j++ ) {
      act_sum[idx] = i + j; 
      idx++;
    }
  }
  
  int err = 0;
  for (int i = 0; i < 25; i ++) {
    std::cout << " (" << i << ") act_sum = " << act_sum[i] <<
                 "sum = " << sum_array[i] << "\n";

    if (act_sum[i] != sum_array[i] ){
      err++;
    }
  }

  //------------------------------------------------------------ 
  // Write out root mean squared error (RMSE) of error ratios
  //------------------------------------------------------------ 
  // Print to screen
  std::cout << "#------------------------------------------------\n"
            << "Number of errors = " << err << "\n"
            << "#------------------------------------------------\n";

  return 0;
}
