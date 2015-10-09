//========================================================================
// PolyDsuListHLS.cc
//========================================================================
// Author  : Shreesha Srinath
// Date    : July 09, 2015
//
// C++ implementation of the list data-structure unit. The list
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#include "PolyDsuListHLS.h"

using namespace xmem;
using namespace polydsu;

//------------------------------------------------------------------------
// insert method
//------------------------------------------------------------------------

List::iterator insert( List::const_iterator pos,
                       List::iterator::pointer new_node,
                       const int& val )
{
  List::iterator::pointer p = pos.get_ptr();

  List::node_ptr prev = p->m_prev;
  
  new_node->m_value = val;
  new_node->m_next  = p;
  new_node->m_prev  = prev;

  prev->m_next      = new_node;
  p->m_prev         = new_node;

  return List::iterator( new_node );
}

//------------------------------------------------------------------------
// PolyDsuListHLS
//------------------------------------------------------------------------

void PolyDsuListHLS(
  hls::stream<PolyDsuReqMsg>&   xcelreq,
  hls::stream<PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&           memreq,
  xmem::MemRespStream&          memresp
)
{

#pragma HLS pipeline II=1
#pragma HLS latency max=1

  // Local variables
  //MemRespMsg<>  mem_resp;
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
    list_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    unsigned value = node.m_value;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), value ) );
    go = false;
  }
  // store request
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_SET ) {
    list_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    node.m_value = xcel_req.data();
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), xcel_req.addr(), 0 ) );
    go = false;
  }
  // increment address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_INCR ) {
    list_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    list_node_ptr next = node.m_next;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), next.get_addr(), 0 ) );
    go = false;
  }
  // decrement address
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_DECR ) {
    list_node node( xcel_req.addr(), xcel_req.opq(), memreq, memresp );
    list_node_ptr prev = node.m_prev;
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), prev.get_addr(), 0 ) );
    go = false;
  }
  // insert method
  else if ( xcel_req.opc() == PolyDsuReqMsg::TYPE_MFX ) {
    ap_uint<32> result = insert(
            List::const_iterator( List::iterator::pointer( xregs[1], xcel_req.opq(), memreq, memresp )),
            List::iterator::pointer( xregs[2], xcel_req.opq(), memreq, memresp ),
            xregs[3]
        ).get_ptr().get_addr();
    xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), result ) );
    go = false;
  }

}


