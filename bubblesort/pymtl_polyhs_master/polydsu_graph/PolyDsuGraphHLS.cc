//========================================================================
// PolyDsuGraphHLS.cc
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

#include "PolyDsuGraphHLS.h"

using namespace xmem;
using namespace polydsu;

//------------------------------------------------------------------------
// PolyDsuGraphHLS
//------------------------------------------------------------------------

void PolyDsuGraphHLS(
  hls::stream<PolyDsuReqMsg>&   xcelreq,
  hls::stream<PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&           memreq,
  xmem::MemRespStream&          memresp
)
{

#pragma HLS pipeline II=1
#pragma HLS latency max=1

  // Local variables
  bool          go = false;
  PolyDsuReqMsg xcel_req;

  // State
  ap_uint<32>  xregs[4];

  // Configure
  while ( !go ) {
    xcel_req = xcelreq.read();
    if ( xcel_req.opc() != PolyDsuReqMsg::TYPE_MTX ) {
      go = true;
      break;
    }
    ap_wait();
    ap_wait();
    xregs[ xcel_req.raddr() ] = xcel_req.rdata();
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), 0 ) );
  }

  // load request
  if      ( xcel_req.opc() == PolyDsuReqMsg::TYPE_GET ) {
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // store request
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_SET ) {
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // increment address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_INCR ) {
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // decrement address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_DECR ) {
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // insert method
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_MFX ) {
    Graph g( xregs[1], xregs[2], xcel_req.opq(), memreq, memresp );
    bool success =
      g.bellman_ford( Graph::vertex_iterator( xregs[3], xcel_req.opq(), memreq, memresp ) );

    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), success? 1:0 ) );
    go = false;
  }

}


