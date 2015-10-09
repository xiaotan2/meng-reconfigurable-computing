//========================================================================
// HashMapInsertHLS.t.cc
//========================================================================

#include "utst/utst.h"
#include "polydsu_hashmap/HashMapInsertHLS.h"

using namespace xmem;
using namespace polydsu;

// Global Constants
const unsigned opc_mfx  = PolyDsuReqMsg::TYPE_MFX;
const unsigned opc_mtx  = PolyDsuReqMsg::TYPE_MTX;

//-----------------------------------------------------------------------
// Struct to hold the arguments for 1 insert operation
//-----------------------------------------------------------------------
struct insert_args {
  unsigned key;
  unsigned val;
  unsigned new_entry;
  unsigned table_ptr;

  insert_args( unsigned key_, unsigned val_, unsigned entry, unsigned tbl_ptr )
    : key( key_ ), val( val_ ), new_entry( entry ), table_ptr( tbl_ptr )
  {}
};

//-----------------------------------------------------------------------
// Perform a series of inserts
//-----------------------------------------------------------------------
void run_test( const unsigned                  base_addr,
               const unsigned                  table_addr,
               const std::vector<unsigned>&    mem,
               const std::vector<insert_args>& msgs,
               const std::vector<int>&         hashmap_ref,
               bool  dump_mem = false
             )
{
  // Processor configuration streams
  hls::stream<PolyDsuReqMsg>  xcelreq;
  hls::stream<PolyDsuRespMsg> xcelresp;

  // Initialize memory array
  TestMem test_mem;
  for ( unsigned i = 0; i < mem.size(); ++i ) {
    test_mem.mem_write( base_addr + i*4, mem[i] );
  }

  for (unsigned i = 0; i < msgs.size(); ++i) {
    insert_args args = msgs[i];

    // Write configuration msgs
    //                            id  opq opc      raddr data
    xcelreq.write( PolyDsuReqMsg( 0,  0,  opc_mtx, 1,    args.key       ) );  // key
    xcelreq.write( PolyDsuReqMsg( 0,  0,  opc_mtx, 2,    args.val       ) );  // value
    xcelreq.write( PolyDsuReqMsg( 0,  0,  opc_mtx, 3,    args.new_entry ) );  // new_entry
    xcelreq.write( PolyDsuReqMsg( 0,  0,  opc_mtx, 4,    args.table_ptr ) );  // table_ptr
    xcelreq.write( PolyDsuReqMsg( 0,  0,  opc_mfx, 0,    0              ) );  // read result

    // Call hashmap insert
    HashMapInsertHLS( xcelreq, xcelresp, test_mem, test_mem );

    // Drain responses to configuration msgs
    xcelresp.read();
    xcelresp.read();
    xcelresp.read();
    xcelresp.read();

    // Final response should contain a pointer to the inserted node
    PolyDsuRespMsg resp = xcelresp.read();
    UTST_CHECK_EQ( resp.rdata(), hashmap_ref[i] );
  }

  // verify the contents in the hash table
  if ( dump_mem ) {
    for ( unsigned i = 0; i < hashmap_ref.size(); ++i ) {
      unsigned table_offset = hashmap_ref[i] * 4;
      unsigned addr = test_mem.mem_read( table_addr + table_offset );

      unsigned next = test_mem.mem_read( addr );
      unsigned key   = test_mem.mem_read( addr+4 );
      unsigned value = test_mem.mem_read( addr+8 );

      std::cout << "Node " << i << " :\n";
      std::cout << "  next: " << next << "\n";
      std::cout << "  key : " << key << "\n";
      std::cout << "  val : " << value << "\n";
    }
  }

}

UTST_AUTO_TEST_CASE( Insert )
{

  const unsigned Base = 4;

  // initialize nodes in memory
  std::vector<unsigned> mem;
  mem.push_back(    0 );
  mem.push_back(    1 );
  mem.push_back( 1000 );

  mem.push_back(    0 );
  mem.push_back(    2 );
  mem.push_back( 2000 );

  mem.push_back(    0 );
  mem.push_back( 2000 );
  mem.push_back( 2001 );

  mem.push_back(    0 );
  mem.push_back(   16 );
  mem.push_back( 1600 );

  // xcel msgs
  std::vector<insert_args> msgs;
  //                            key  value node     table_ptr
  msgs.push_back( insert_args(    1, 1000, Base+0,  Base+48 ) );
  msgs.push_back( insert_args(    2, 2000, Base+12, Base+48 ) );
  msgs.push_back( insert_args( 2000, 2001, Base+24, Base+48 ) );
  msgs.push_back( insert_args(   16, 1600, Base+36, Base+48 ) );

  // expected results
  std::vector<int> hashmap_ref;
  hashmap_ref.push_back( 1 );
  hashmap_ref.push_back( 7 );
  hashmap_ref.push_back( 2 );
  hashmap_ref.push_back( 1 );

  run_test( Base, Base+48, mem, msgs, hashmap_ref );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_hashmap" );
}

