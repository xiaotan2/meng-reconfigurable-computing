//=========================================================================
// pageRank.cpp
//=========================================================================
// @brief : A PAGERANK implementation of sine and cosine functions.

#include <hls_stream.h>
#include <iostream>
#include "pageRank.h"

//-----------------------------------
// dut function (top module)
//-----------------------------------
// @param[in]  : strm_in - input stream
// @param[out] : strm_out - output stream 
void dut (
    hls::stream<bit32_t> &strm_in,
    hls::stream<bit32_t> &strm_out
)
{
  bit32_t sum, a, b;

  // ------------------------------------------------------
  // Input processing
  // ------------------------------------------------------
  // Read the two input 32-bit words (low word first)
  a = strm_in.read();
  b = strm_in.read();

  // ------------------------------------------------------
  // Call PAGERANK 
  // ------------------------------------------------------
  pageRank( sum, a, b );

  // ------------------------------------------------------
  // Output processing
  // ------------------------------------------------------
  // Write out the cos value (low word first)
  strm_out.write( sum );
}


//-----------------------------------
// pageRank function
//-----------------------------------
// @param[in]  : a - operand 1, 32 bit uint
// @param[in]  : b - operand 2, 32 bit uint
// @param[out] : c - sum,       32 bit uint
void pageRank(bit32_t &sum, bit32_t a, bit32_t b)
{
  sum = a + b;

//  std::cout << "a = " << a << "\n" <<
//               "b = " << b << "\n" <<
//               "s = " << sum << "\n";
}
