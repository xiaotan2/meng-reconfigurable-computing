//=========================================================================
// cordic.h
//=========================================================================
 
#ifndef CORDIC_H
#define CORDIC_H

#include <hls_stream.h>

#include "typedefs.h"

// Top function for synthesis
void dut (
    hls::stream<bit32_t> &strm_in,
    hls::stream<bit32_t> &strm_out
);

// Top function for CORDIC
void cordic (
    bit32_t &sum,
    bit32_t a,
    bit32_t b
);

#endif
