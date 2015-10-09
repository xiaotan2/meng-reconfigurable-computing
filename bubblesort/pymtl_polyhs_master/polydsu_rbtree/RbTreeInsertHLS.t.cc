//========================================================================
// RbTreeInsertHLS.t.cc
//========================================================================

#include "utst/utst.h"
#include "polydsu_rbtree/RbTreeInsertHLS.h"

#include <vector>
#include <algorithm>

using namespace xmem;
using namespace xcel;

//------------------------------------------------------------------------
// Helper struct to hold xcel arguments
//------------------------------------------------------------------------
struct insert_args {
  unsigned header;
  unsigned node;
  unsigned key;

  insert_args( unsigned _header, unsigned _node, unsigned _key )
    : header( _header ), node( _node ), key( _key )
  {}
};

//------------------------------------------------------------------------
// Helper function
//------------------------------------------------------------------------
void run_test( const unsigned Base,
               const std::vector<int>& mem,
               const std::vector<Key>& tree_ref,
               const std::vector<insert_args>& msgs,
               const bool dump_mem = false)
{
  // Processor configuration streams
  hls::stream<XcelReqMsg>  xcelreq;
  hls::stream<XcelRespMsg> xcelresp;

  // Test memory
  TestMem test_mem;

  // Initialize memory array
  for (unsigned i = 0;i < mem.size(); ++i) {
    test_mem.mem_write( Base+(4*i), mem[i] );
  }

  for (unsigned i = 0; i < msgs.size(); ++i) {
    insert_args args = msgs[i];

    // Write configuration msgs
    //                         opq type addr  data          id
    xcelreq.write( XcelReqMsg( 0,  1,   1,    args.header,  0 ) );  // tree header
    xcelreq.write( XcelReqMsg( 0,  1,   2,    args.node,    0 ) );  // new node
    xcelreq.write( XcelReqMsg( 0,  1,   3,    args.key,     0 ) );  // key
    xcelreq.write( XcelReqMsg( 0,  1,   0,    0x0,          0 ) );  // start
    xcelreq.write( XcelReqMsg( 0,  0,   0,    0x0,          0 ) );  // read result

    // Call list insert
    RbTreeInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    RbTreeInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    RbTreeInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    RbTreeInsertHLS( xcelreq, xcelresp, test_mem, test_mem );
    RbTreeInsertHLS( xcelreq, xcelresp, test_mem, test_mem );

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
  NodePtr header( msgs[0].header, test_mem, test_mem );
  Tree::iterator first( header->m_left );
  // get iterator to end, which is header
  Tree::iterator last ( header );
  // Iterate through the list and check against tree_ref
  unsigned i = 0;
  for (; first != last; ++first) {
    int node_data = first.key();
    //printf ("Node :%d\n", node_data);
    UTST_CHECK_EQ( node_data, tree_ref[i++] );
  }

  // print out the memory
  if (dump_mem) {
    printf ("Final Memory Layout:\n");
    for (unsigned i = 0;i < mem.size(); ++i) {
      int address = Base+(4*i);
      printf ("%3d: %3d\n", address, test_mem.mem_read( address ));
    }
  }
}

//--------------------------------------------------------------
// InsertMini
//--------------------------------------------------------------
UTST_AUTO_TEST_CASE( InsertMini )
{
  const unsigned Base = 2000;
  const int N = 4;

  std::vector<int> mem;
  mem.push_back( 0x0);          // header node parent (Null)
  mem.push_back( Base );        // left   (points to Base)
  mem.push_back( Base );        // right  (points to Base)
  mem.push_back( 0x0 );         // color  (red)
  mem.push_back( 0xff );        // key
  mem.push_back( 0xff );        // value

  // 4 nodes worth of memory
  // The nodes are at +24, +48, +72, +96
  for (int i = 0; i < N; ++i) {
    mem.push_back( 0xff );      // base
    mem.push_back( 0xff );      // left
    mem.push_back( 0xff );      // right
    mem.push_back( 0xff );      // color
    mem.push_back( 0xff );      // key
    mem.push_back( 0xff );      // value
  }

  // tree is always sorted, so push in reference data in order
  std::vector<Key> tree_ref;
  for (int i = 0; i < N; ++i) {
    tree_ref.push_back( i+1 );
  }

  std::vector<insert_args> msgs;
  //                      header  node_mem  data
  msgs.push_back( insert_args( Base+0,  Base+24, 2 ) );
  msgs.push_back( insert_args( Base+0,  Base+48, 3 ) );
  msgs.push_back( insert_args( Base+0,  Base+72, 1 ) );
  msgs.push_back( insert_args( Base+0,  Base+96, 4 ) );

  run_test( Base, mem, tree_ref, msgs );
}

//--------------------------------------------------------------
// InsertRandom
//--------------------------------------------------------------
UTST_AUTO_TEST_CASE( InsertRandom )
{
  const unsigned Base = 1000;
  const int N = 20;

  std::vector<int> mem;
  mem.push_back( 0x0);          // header node parent (Null)
  mem.push_back( Base );        // left   (points to Base)
  mem.push_back( Base );        // right  (points to Base)
  mem.push_back( 0x0 );         // color  (red)
  mem.push_back( 0xff );        // key
  mem.push_back( 0xff );        // value

  // 4 nodes worth of memory
  // The nodes are at +24, +48, +72, +96
  for (int i = 0; i < N; ++i) {
    mem.push_back( 0xff );      // base
    mem.push_back( 0xff );      // left
    mem.push_back( 0xff );      // right
    mem.push_back( 0xff );      // color
    mem.push_back( 0xff );      // key
    mem.push_back( 0xff );      // value
  }

  std::vector<Key> tree_ref;
  for (int i = 0; i < N; ++i) {
    Key x = 0;
    do {
      x = rand() % 0x6000;
    } while( find( tree_ref.begin(), tree_ref.end(), x) != tree_ref.end() );

    tree_ref.push_back( x );
  }

  std::vector<insert_args> msgs;
  //                            header  node_mem  data
  for (int i = 0; i < N; ++i) {
    msgs.push_back( insert_args( Base+0,  Base+(i+1)*24, tree_ref[i] ) );
  }

  std::sort( tree_ref.begin(), tree_ref.end() );

  run_test( Base, mem, tree_ref, msgs );
}


//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "rbtree_insert" );
}

