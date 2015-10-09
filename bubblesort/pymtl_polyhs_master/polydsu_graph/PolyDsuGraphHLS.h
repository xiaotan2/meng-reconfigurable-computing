//========================================================================
// PolyDsuGraphHLS.h
//========================================================================
// Author  : Ritchie Zhao
// Date    : Sept 07, 2015
//
// C++ implementation of the graph data-structure unit. The graph
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#ifndef POLYDSU_GRAPH_POLY_DSU_GRAPH_HLS_H
#define POLYDSU_GRAPH_POLY_DSU_GRAPH_HLS_H

#include <ap_utils.h>
#include <hls_stream.h>

#include "xmem/MemMsg.h"
#include "polydsu/PolyDsuCommon.h"
#include "polydsu/PolyDsuMsg.h"

#include "polydsu_graph/Graph.h"
#include "polydsu_graph/GraphProxy.h"

typedef _Graph<int> Graph;

//------------------------------------------------------------------------
// PolyDsuGraphHLS
//------------------------------------------------------------------------

void PolyDsuGraphHLS(
  hls::stream<polydsu::PolyDsuReqMsg>&   xcelreq,
  hls::stream<polydsu::PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&                    memreq,
  xmem::MemRespStream&                   memresp
);

#endif /* POLYDSU_GRAPH_POLY_DSU_GRAPH_HLS_H */

