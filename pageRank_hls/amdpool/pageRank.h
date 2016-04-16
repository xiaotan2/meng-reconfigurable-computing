//=========================================================================
// pageRank.h
//=========================================================================
 
#ifndef PAGERANK_H
#define PAGERANK_H

#include <hls_stream.h>

#include "typedefs.h"

// Top function for synthesis
void dut (
    hls::stream<bit32_t> &strm_in,
    hls::stream<bit32_t> &strm_out
);

// Top function for PAGERANK
void pageRank (
    bit32_t &sum,
    bit32_t a,
    bit32_t b
);

#endif
