#include "utst/utst.h"
#include "polydsu_rbtree/PolyDsuRbTreeHLS.h"

using namespace xmem;
using namespace polydsu;

// Global Constants
const unsigned opc_get  = PolyDsuReqMsg::TYPE_GET;
const unsigned opc_set  = PolyDsuReqMsg::TYPE_SET;
const unsigned opc_incr = PolyDsuReqMsg::TYPE_INCR;
const unsigned opc_decr = PolyDsuReqMsg::TYPE_DECR;
const unsigned opc_mfx  = PolyDsuReqMsg::TYPE_MFX;
const unsigned opc_mtx  = PolyDsuReqMsg::TYPE_MTX;

// Global test vector
// 72 -> 24 -> 48 -> 96
const int g_rbtree_mem[] = {
  24,   72,   96,   0,  255,  255,    //  0, header
  0,    72,   48,   1,    2,    2,    // 24, parent is header node1
  24,   0,    96,   1,    3,    3,    // 48 node2
  24,   0,     0,   1,    1,    1,    // 72 node3
  48,   0,     0,   0,    4,    4,    // 96 node4
};

//-----------------------------------------------------------------------
// Performs a single operation.
// Used for get, set, incr, decr
//-----------------------------------------------------------------------
PolyDsuRespMsg xcel_op(
    TestMem& test_mem,
    const unsigned opc,
    const unsigned addr,
    const unsigned data
){
  // Processor configuration streams
  hls::stream<PolyDsuReqMsg>   xcelreq;
  hls::stream<PolyDsuRespMsg>  xcelresp;

  // write request to xcelreq
  //                           id opq  opc  addr  data iter
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc, addr, data,   0 ) );

  // Call the xcel
  PolyDsuRbTreeHLS( xcelreq, xcelresp, test_mem, test_mem );

  return xcelresp.read();
}

//-----------------------------------------------------------------------
// Performs a single insert operation
//-----------------------------------------------------------------------
PolyDsuRespMsg xcel_insert(
    TestMem& test_mem,
    const unsigned header_addr,     // tree header node
    const unsigned node_addr,       // new node
    const int key
){
  // Processor configuration streams
  hls::stream<PolyDsuReqMsg>   xcelreq;
  hls::stream<PolyDsuRespMsg>  xcelresp;

  // write requests to xcelreq
  //                           id opq  opc    raddr       data
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  1, header_addr ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  2,   node_addr ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  3,         key ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mfx,  0,           0 ) );

  PolyDsuRbTreeHLS( xcelreq, xcelresp, test_mem, test_mem );

  xcelresp.read();
  xcelresp.read();
  xcelresp.read();
  return xcelresp.read();
}

//-----------------------------------------------------------------------
// TestGetSet
//-----------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestGetSet )
{
  const unsigned Base = 2000;

  // create and load test memory
  TestMem test_mem;
  for (unsigned i = 0;i < sizeof(g_rbtree_mem)/sizeof(int); ++i) {
    test_mem.mem_write( Base+(4*i), g_rbtree_mem[i] );
  }

  // test get
  UTST_CHECK_EQ( 2, xcel_op( test_mem, opc_get, Base+24, 0 ).data() );
  UTST_CHECK_EQ( 3, xcel_op( test_mem, opc_get, Base+48, 0 ).data() );
  UTST_CHECK_EQ( 1, xcel_op( test_mem, opc_get, Base+72, 0 ).data() );
  UTST_CHECK_EQ( 4, xcel_op( test_mem, opc_get, Base+96, 0 ).data() );

  // test set
  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+24, 4 ).data() );
  UTST_CHECK_EQ( 4, xcel_op( test_mem, opc_get, Base+24, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+48, 5 ).data() );
  UTST_CHECK_EQ( 5, xcel_op( test_mem, opc_get, Base+48, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+72, 9 ).data() );
  UTST_CHECK_EQ( 9, xcel_op( test_mem, opc_get, Base+72, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+96, 8 ).data() );
  UTST_CHECK_EQ( 8, xcel_op( test_mem, opc_get, Base+96, 0 ).data() );
}

//-----------------------------------------------------------------------
// TestIncrDecr
//-----------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestIncrDecr )
{
  const unsigned Base = 0x81B0;

  // create and load test memory
  TestMem test_mem;
  for (unsigned i = 0;i < sizeof(g_rbtree_mem)/sizeof(int); ++i) {
    test_mem.mem_write( Base+(4*i), g_rbtree_mem[i] );
  }

  // test incr
  UTST_CHECK_EQ( 24, xcel_op( test_mem, opc_incr, Base+72, 0).addr() );
  UTST_CHECK_EQ( 48, xcel_op( test_mem, opc_incr, Base+24, 0).addr() );
  UTST_CHECK_EQ( 96, xcel_op( test_mem, opc_incr, Base+48, 0).addr() );

  // test decr
  UTST_CHECK_EQ( 48, xcel_op( test_mem, opc_decr, Base+96, 0).addr() );
  UTST_CHECK_EQ( 24, xcel_op( test_mem, opc_decr, Base+48, 0).addr() );
  UTST_CHECK_EQ( 72, xcel_op( test_mem, opc_decr, Base+24, 0).addr() );

  // dump memory
  /*for (unsigned i = 0;i < sizeof(g_rbtree_mem)/sizeof(int); ++i) {
    int data = test_mem.mem_read( Base+4*i );
    printf ("%4x: %2d\n", Base+4*i, data);
  }*/
}

//-----------------------------------------------------------------------
// TestInsert
//-----------------------------------------------------------------------
// We build the test_mem list from a single node
UTST_AUTO_TEST_CASE( TestInsert )
{
  const unsigned Base = 1000;

  // create and load test memory
  // here we just create a single element list, which is
  // a node with prev and next pointing to itself
  TestMem test_mem;
  rbtree_node_ptr ptr( Base, 0, test_mem, test_mem );
  ptr->m_parent = 0;
  ptr->m_left   = Base;
  ptr->m_right  = Base;
  ptr->m_color  = 0;

  UTST_CHECK_EQ( Base+96, xcel_insert( test_mem,  Base+0, Base+96, 4 ).addr() );
  UTST_CHECK_EQ(       0, xcel_op    ( test_mem, opc_set, Base+96, 4 ).data() );
  UTST_CHECK_EQ( Base+24, xcel_insert( test_mem,  Base+0, Base+24, 2 ).addr() );
  UTST_CHECK_EQ(       0, xcel_op    ( test_mem, opc_set, Base+24, 2 ).data() );
  UTST_CHECK_EQ( Base+48, xcel_insert( test_mem,  Base+0, Base+48, 3 ).addr() );
  UTST_CHECK_EQ(       0, xcel_op    ( test_mem, opc_set, Base+48, 3 ).data() );
  UTST_CHECK_EQ( Base+72, xcel_insert( test_mem,  Base+0, Base+72, 1 ).addr() );
  UTST_CHECK_EQ(       0, xcel_op    ( test_mem, opc_set, Base+72, 1 ).data() );

  // dump mem
  /*for (int i = 0; i < 6*5; ++i) {
    int d = test_mem.mem_read( Base+4*i );
    printf ("%2d: %2d\n", 4*i, d);
  }*/

  // check memory by iterating through the list
  rbtree::iterator::pointer p( Base, 0, test_mem, test_mem );
  rbtree::iterator first( p->m_left );
  rbtree::iterator last( p );
  int i = 0;
  for (; first != last; ++first) {
    int node_data = *first;
    UTST_CHECK_EQ( node_data, ++i );
  }
  UTST_CHECK_EQ( i, 4 );
}

//-----------------------------------------------------------------------
// InsertStoreCount
//-----------------------------------------------------------------------
// Count number of stores on an insert
UTST_AUTO_TEST_CASE( InsertStoreCount )
{
  const unsigned Base = 40;
  const int N = 1000;

  TestMem test_mem;
  rbtree_node_ptr ptr( Base, 0, test_mem, test_mem );
  ptr->m_parent = 0;
  ptr->m_left   = Base;
  ptr->m_right  = Base;
  ptr->m_color  = 0;

  int max_stores = 0;
  int max_i = 0;

  int total_stores = 0;
  int total_loads = 0;

  for (int i = 0; i < N; ++i) {
    int node_addr = Base+i*4*6;

    test_mem.clear_num_requests();

    xcel_insert( test_mem, Base, node_addr, i );

    int stores = test_mem.get_num_stores();
    int loads = test_mem.get_num_loads();
    total_stores += stores;
    total_loads += loads;

    if (stores > max_stores) {
      max_stores = stores;
      max_i = i;
    }
  }

  printf ("---------------------------------------------\n");
  printf ("Rbtree insert: max stores is %d on insert #%d\n", max_stores, max_i);
  printf ("               avg stores is %4.2f\n", (float)total_stores/N);
  printf ("               avg loads  is %4.2f\n", (float)total_loads/N);
  printf ("---------------------------------------------\n");
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------
int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_rbtree" );
}

