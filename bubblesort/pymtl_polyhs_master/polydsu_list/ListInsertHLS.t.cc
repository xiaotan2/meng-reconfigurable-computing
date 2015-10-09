//========================================================================
// ListInsertHLS.t.cc
//========================================================================

#include "utst/utst.h"
#include "polydsu_list/ListInsertHLS.h"

using namespace xmem;
using namespace xcel;

//-----------------------------------------------------------------------
// Struct to hold the arguments for 1 insert operation
//-----------------------------------------------------------------------
struct insert_args {
  int pos;
  int node;
  int val;

  insert_args( int _pos, int _node, int _val )
    : pos( _pos ), node( _node ), val( _val )
  {}
};

//-----------------------------------------------------------------------
// Perform a series of inserts
//-----------------------------------------------------------------------
void run_test( const unsigned base_addr,
               const std::vector<int>& mem,
               const std::vector<int>& list_ref,
               const std::vector<insert_args>& msgs,
               const bool dump_mem = false)
{
  // Processor configuration streams
  hls::stream<XcelReqMsg>  xcelreq;
  hls::stream<XcelRespMsg> xcelresp;

  TestMem test_mem;

  // Initialize memory array
  for (unsigned i = 0;i < mem.size(); ++i) {
    test_mem.mem_write( base_addr+(4*i), mem[i] );
  }

  for (unsigned i = 0; i < msgs.size(); ++i) {
    insert_args args = msgs[i];

    // Write configuration msgs
    //                         opq type addr  data       id
    xcelreq.write( XcelReqMsg( 0,  1,   1,    args.pos,  0 ) );  // node pos
    xcelreq.write( XcelReqMsg( 0,  1,   2,    args.node, 0 ) );  // new node
    xcelreq.write( XcelReqMsg( 0,  1,   3,    args.val,  0 ) );  // val
    xcelreq.write( XcelReqMsg( 0,  1,   0,    0x0,       0 ) );  // start
    xcelreq.write( XcelReqMsg( 0,  0,   0,    0x0,       0 ) );  // read result

    // Call list insert
    ListInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    ListInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    ListInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    ListInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    ListInsertHLS( xcelreq, xcelresp, test_mem, test_mem );

    // Drain responses to configuration msgs
    xcelresp.read();
    xcelresp.read();
    xcelresp.read();
    xcelresp.read();

    // Final response should contain a pointer to the inserted node
    XcelRespMsg resp = xcelresp.read();
    UTST_CHECK_EQ( resp.data(), args.node );
  }

  // get iterator to beginning, which is header->next
  List::iterator::pointer p( base_addr, test_mem, test_mem );
  List::iterator first( p );
  first++;
  // get iterator to end, which is header
  List::iterator last( p );
  // Iterate through the list and check against list_ref
  unsigned i = 0;
  for (; first != last; ++first) {
    int node_data = *first;
    //printf ("Node :%d\n", node_data);
    UTST_CHECK_EQ( node_data, list_ref[i++] );
  }

  // print out the memory
  if( dump_mem ) {
    printf ("Final Memory Layout:\n");
    for (unsigned i = 0;i < mem.size(); ++i) {
      int address = base_addr+(4*i);
      printf ("%3d: %3d\n", address, test_mem.mem_read( address ));
    }
  }
}

//--------------------------------------------------------------
// InsertBegin
//   Inserts a bunch of nodes to the beginning of the list
//--------------------------------------------------------------
UTST_AUTO_TEST_CASE( InsertBegin )
{
  const unsigned Base = 2000;

  std::vector<int> mem;
  mem.push_back( Base );        // 0
  mem.push_back( Base );
  mem.push_back( 9999 );
  mem.push_back( 0xff );        // 12
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 24
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 36
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 48
  mem.push_back( 0xff );
  mem.push_back( 0xff );

  std::vector<int> list_ref;
  list_ref.push_back( 1 );
  list_ref.push_back( 2 );
  list_ref.push_back( 3 );
  list_ref.push_back( 4 );

  std::vector<insert_args> msgs;
  //                    insert_at  node_mem  data
  msgs.push_back( insert_args( Base+0,  Base+24,    4 ) );
  msgs.push_back( insert_args( Base+24, Base+12,    3 ) );
  msgs.push_back( insert_args( Base+12, Base+48,    2 ) );
  msgs.push_back( insert_args( Base+48, Base+36,    1 ) );

  run_test( Base, mem, list_ref, msgs );
}

UTST_AUTO_TEST_CASE( InsertEnd )
{
  const unsigned Base = 2000;

  std::vector<int> mem;
  mem.push_back( Base );        // 0
  mem.push_back( Base );
  mem.push_back( 9999 );
  mem.push_back( 0xff );        // 12
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 24
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 36
  mem.push_back( 0xff );
  mem.push_back( 0xff );
  mem.push_back( 0xff );        // 48
  mem.push_back( 0xff );
  mem.push_back( 0xff );

  std::vector<int> list_ref;
  list_ref.push_back( 1 );
  list_ref.push_back( 2 );
  list_ref.push_back( 3 );
  list_ref.push_back( 4 );

  std::vector<insert_args> msgs;
  //                    insert_at  node_mem  data
  msgs.push_back( insert_args( Base+0,  Base+12,    1 ) );
  msgs.push_back( insert_args( Base+0,  Base+36,    2 ) );
  msgs.push_back( insert_args( Base+0,  Base+24,    3 ) );
  msgs.push_back( insert_args( Base+0,  Base+48,    4 ) );

  run_test( Base, mem, list_ref, msgs );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_list" );
}

