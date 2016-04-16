#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<fcntl.h>
#include<math.h>
#include<assert.h>

#include<iostream>
#include<fstream>

#include "host.h"
#include "timer.h"

//--------------------------------------
// main function
//--------------------------------------
int main(int argc, char** argv)
{
  // Open channels to the FPGA board.
  // These channels appear as files to the Linux OS
  int fdr = open("/dev/xillybus_read_32", O_RDONLY);
  int fdw = open("/dev/xillybus_write_32", O_WRONLY);

  // Check that the channels are correctly opened
  if ((fdr < 0) || (fdw < 0)) {
    fprintf (stderr, "Failed to open Xillybus device channels\n");
    exit(-1);
  }

  // arrays to store the output
  int sum_array[NUM_OUTPUT];
  
  int nbytes;
  
  Timer timer("CORDIC fpga (batch)");

  timer.start();

  //----------------------------------------------------------------------
  // Send all values to the module
  //----------------------------------------------------------------------
  for (int i = 0; i < NUM_INPUT; ++i) {
    for (int j = 0; j < NUM_INPUT; ++i) {
	  int32_t a, b;
      a = i;
      // Send bytes through the write channel
      // and assert that the right number of bytes were sent
      nbytes = write (fdw, (void*)&a, sizeof(a));
      assert (nbytes == sizeof(a));
	  
	  b = j;
      // Send bytes through the write channel
      // and assert that the right number of bytes were sent
      nbytes = write (fdw, (void*)&b, sizeof(b));
      assert (nbytes == sizeof(b));
	}
  }

  //----------------------------------------------------------------------
  // Read all results
  //----------------------------------------------------------------------
  for (int i = 1; i < NUM_OUTPUT; ++i) {
    // Receive bytes through the read channel
    // and assert that the right number of bytes were recieved
    int32_t sum_out;
    nbytes = read (fdr, (void*)&sum_out, sizeof(sum_out));
    assert (nbytes == sizeof(sum_out));

    // Store to array
    sum_array[i] = sum_out;
  }

  timer.stop();
  
  //------------------------------------------------------------ 
  // Check results
  //------------------------------------------------------------ 
  int idx = 0;
  int act_sum[NUM_OUTPUT];
  for (int i = 0; i < NUM_INPUT; i++) {
    for ( int j = 0; j < NUM_INPUT; j++ ) {
      act_sum[idx] = i + j;
      idx++;
    }
  }
  
  // error number
  int err = 0;
  for (int i = 0; i < NUM_OUTPUT; i ++) {
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

  // Clean up
  close(fdr);
  close(fdw);

  return 0;
}
