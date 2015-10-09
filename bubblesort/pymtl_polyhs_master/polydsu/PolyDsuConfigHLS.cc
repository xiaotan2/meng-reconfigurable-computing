//========================================================================
// PolyDsuConfigHLS.h
//========================================================================
// Author  : Shreesha Srinath
// Date    : July 09, 2015
//
//
// C++ implementation of the data-structure unit configuration logic.
// The unit receives a configuration message and sets state for the
// data-structure unit. The state that stores data-structure/
// data-type descriptors and the data-structre type.
//
// NOTE: The design currently supports only primitive data-types.

#include "polydsu/PolyDsuConfigHLS.h"

using namespace polydsu;

//------------------------------------------------------------------------
// dsuTable::dsuTable
//------------------------------------------------------------------------

dsuTable::dsuTable()
{
  #pragma HLS resource variable=table core=RAM_2P_1S
  for ( ap_uint<6> i = 0; i < NumDsuEntries; ++i )
    table[i] = 0;
}

//------------------------------------------------------------------------
// dsu::allocate
//------------------------------------------------------------------------

ap_uint<11> dsuTable::allocate( ap_uint<4> dsType, ap_uint<4> dstype[32] )
{
  // XXX: Need to handle the case when all entries are occupies
  for ( ap_uint<5> i = 0; i < NumDsuEntries; ++i ) {
    if ( table[i] == 0 ) {
      table[i]  = 1;
      dstype[i] = dsType;
      return ( 1024 + i );
    }
  }
  return 0;
}

//------------------------------------------------------------------------
// dsu::deallocate
//------------------------------------------------------------------------

void dsuTable::deallocate( ap_uint<5> dsId )
{
  table[dsId] = 0;
}

//------------------------------------------------------------------------
// PolyDsuConfigHLS
//------------------------------------------------------------------------

void PolyDsuConfigHLS(
  hls::stream<PolyDsuReqMsg>&  xcelreq,
  hls::stream<PolyDsuRespMsg>& xcelresp,
  ap_uint<4>                   dstype[32]
)
{

  // Local variables
  PolyDsuReqMsg xcel_req;

  // Create a dsuTable
  static dsuTable dsTable;

  // Check if a configuration request exists and process it
  if ( !xcelreq.empty() ) {
    xcelreq.read( xcel_req );
    // Allocate
    if      ( xcel_req.raddr() == 1 ) {
      ap_uint<11> ds_id = dsTable.allocate( xcel_req.rdata(), dstype );
      xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), ds_id ) );
    }
    // Deallocte
    else if ( xcel_req.raddr() == 2 ) {
      // NOTE: shreesha: adding two explicit wait statements to force the
      // inputs to be registered. Without the two wait statements the
      // xcelreq.read() and the xcelwrite.resp() operation are scheduled in
      // the same time step and xcelreq.rdy signal is combinationally
      // dependent on the xcelresp.rdy signal. If we integrate this unit to
      // a processor pipeline the design would be stuck in a state as the
      // xcelresp.rdy signal is never asserted to be high until the
      // instruction transitions down to the next stage. I could have
      // solved this by actually adding a single element pipelined queue
      // int the wrapper to register the inputs but that would add an extra
      // cycle to the allocate operation. I could have alternatively added
      // a bypass queue in the wrapper to avoid that edge but instead added
      // the wait statements here by looking into the schedule report to
      // get what I wanted.
      ap_wait();
      ap_wait();
      dsTable.deallocate( xcel_req.rdata() );
      xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), 0 ) );
    }
  }
}


