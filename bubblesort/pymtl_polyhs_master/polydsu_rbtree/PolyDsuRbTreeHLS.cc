//========================================================================
// PolyDsuListHLS.cc
//========================================================================
// Author  : Ritchie Zhao
// Date    : August 24, 2015
//
// C++ implementation of the rbtree data-structure unit. The rbtree
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#include "polydsu_rbtree/PolyDsuRbTreeHLS.h"
#include "polydsu_rbtree/RbTreeInsertHLS.h"

using namespace xmem;
using namespace polydsu;


//------------------------------------------------------------------------
// PolyDsuRbTreeHLS
//------------------------------------------------------------------------

void PolyDsuRbTreeHLS(
  hls::stream<PolyDsuReqMsg>&   xcelreq,
  hls::stream<PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&           memreq,
  xmem::MemRespStream&          memresp
)
{

#pragma HLS pipeline II=1
#pragma HLS latency max=1

  // Local variables
  bool go = false;
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
    rbtree_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    unsigned value = node.m_value;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), value ) );
    go = false;
  }
  // store request
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_SET ) {
    rbtree_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    node.m_value = xcel_req.data();
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // increment address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_INCR ) {
    rbtree::iterator it( rbtree_node_ptr( xcel_req.addr(), xcel_req.opq(), memreq, memresp ) );
    ++it;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    go = false;
  }
  // decrement address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_DECR ) {
    rbtree::iterator it( rbtree_node_ptr( xcel_req.addr(), xcel_req.opq(), memreq, memresp ) );
    --it;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    go = false;
  }
  // insert method
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_MFX ) {
    rbtree::iterator it = insert_unique_hls(
        rbtree::NodePtr( xregs[1], xcel_req.opq(), memreq, memresp ),
        rbtree::NodePtr( xregs[2], xcel_req.opq(), memreq, memresp ),
        xregs[3]
      );
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    go = false;
  }

}

