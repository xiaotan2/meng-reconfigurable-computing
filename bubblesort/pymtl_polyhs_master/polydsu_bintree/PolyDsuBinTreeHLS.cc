//========================================================================
// PolyDsuBinTreeHLS.cc
//========================================================================
// Author  : Ritchie Zhao
// Date    : August 24, 2015
//
// C++ implementation of the bintree data-structure unit. The bintree
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#include "polydsu_bintree/PolyDsuBinTreeHLS.h"

using namespace xmem;
using namespace polydsu;

bintree::iterator
insert_left_hls( bintree_node_ptr x, bintree_node_ptr new_node, int v )
{
  new_node->m_value = v;
  x->m_left = new_node;
  new_node->m_parent = x;
  return bintree::iterator( new_node );
}

bintree::iterator
insert_right_hls( bintree_node_ptr x, bintree_node_ptr new_node, int v )
{
  new_node->m_value = v;
  x->m_right = new_node;
  new_node->m_parent = x;
  return bintree::iterator( new_node );
}

//------------------------------------------------------------------------
// PolyDsuBinTreeHLS
//------------------------------------------------------------------------

void PolyDsuBinTreeHLS(
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
    bintree_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    unsigned value = node.m_value;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), value ) );
    go = false;
  }
  // store request
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_SET ) {
    bintree_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    node.m_value = xcel_req.data();
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // increment address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_INCR ) {
    bintree::inorder_iterator it( bintree_node_ptr( xcel_req.addr(), xcel_req.opq(), memreq, memresp ) );
    ++it;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    go = false;
  }
  // decrement address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_DECR ) {
    bintree::inorder_iterator it( bintree_node_ptr( xcel_req.addr(), xcel_req.opq(), memreq, memresp ) );
    --it;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    go = false;
  }
  // insert method
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_MFX ) {
    if ( xcel_req.addr() == 0 ) {
      bintree::iterator it = insert_left_hls(
          bintree::NodePtr( xregs[1], xcel_req.opq(), memreq, memresp ),
          bintree::NodePtr( xregs[2], xcel_req.opq(), memreq, memresp ),
          xregs[3]
        );
      xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    }
    else {
      bintree::iterator it = insert_right_hls(
          bintree::NodePtr( xregs[1], xcel_req.opq(), memreq, memresp ),
          bintree::NodePtr( xregs[2], xcel_req.opq(), memreq, memresp ),
          xregs[3]
        );
      xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), it.m_node.get_addr(), 0 ) );
    }
    go = false;
  }

}

