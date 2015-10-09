//========================================================================
// HashMapInsertHLS.cc
//========================================================================

#include "polydsu_hashmap/HashMapInsertHLS.h"

using namespace xmem;
using namespace polydsu;

//------------------------------------------------------------------------
// hash_func
//------------------------------------------------------------------------

int hash_func( int key ) {
  int sum = 0;
  unsigned int mask = 1 << ( sizeof( int )*8 - 1 );
  for ( int i = sizeof( int ) * 8 - 1; i >= 0; --i ) {
    int bitslice = ( key & mask ) >> i;
    sum = sum*7 + bitslice;
    mask = mask >> 1;
  }
  return sum % 16;
}

//------------------------------------------------------------------------
// insert
//------------------------------------------------------------------------

template<typename Array>
int insert( const int& key, const int& val,
            HashMapEntryPtr new_entry,
            Array m_table ) {
  int idx = hash_func( key );
  if ( m_table[idx] != 0 ) {
    new_entry->m_next = m_table[idx];
  }
  m_table[idx] = new_entry.get_addr();
  return idx;
}

//------------------------------------------------------------------------
// HashMapInsertHLS
//------------------------------------------------------------------------

void HashMapInsertHLS(
  hls::stream<PolyDsuReqMsg>&   xcelreq,
  hls::stream<PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&           memreq,
  xmem::MemRespStream&          memresp
)
{

  // Local variables
  bool          go = false;
  PolyDsuReqMsg xcel_req;

  // State
  ap_uint<32>  xregs[5];

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

  // Insert
  int idx = insert( xregs[1], xregs[2],
                    HashMapEntryPtr( xregs[3], xcel_req.opq(), memreq, memresp ),
                    ArrayMemPortAdapter<MemReqStream,MemRespStream> (
                      memreq,
                      memresp,
                      xregs[4],
                      0
                    ) );

  // Done
  xcelresp.write( PolyDsuRespMsg( xcel_req.id(), xcel_req.opq(), xcel_req.opc(), idx ) );
  go = false;

}
