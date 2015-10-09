//========================================================================
// PolyDsuListHLS.t.cc
//========================================================================

#include "utst/utst.h"
#include "polydsu_list/PolyDsuListHLS.h"

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
// 0 -> 36 -> 48 -> 12 -> 24
const int g_list_mem[] = {
  24, 36,  0,       // 0
  48, 24,  3,       // 12
  12,  0,  4,       // 24
   0, 48,  1,       // 36
  36, 12,  2        // 48
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
  PolyDsuListHLS( xcelreq, xcelresp, test_mem, test_mem );

  return xcelresp.read();
}

//-----------------------------------------------------------------------
// Performs a single insert operation
//-----------------------------------------------------------------------
PolyDsuRespMsg xcel_insert(
    TestMem& test_mem,
    const unsigned insert_addr,     // node to insert at
    const unsigned node_addr,       // new node
    const int val
){
  // Processor configuration streams
  hls::stream<PolyDsuReqMsg>   xcelreq;
  hls::stream<PolyDsuRespMsg>  xcelresp;

  // write requests to xcelreq
  //                           id opq  opc    raddr       data
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  1, insert_addr ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  2,   node_addr ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  3,         val ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mfx,  0,           0 ) );

  PolyDsuListHLS( xcelreq, xcelresp, test_mem, test_mem );

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
  for (unsigned i = 0;i < sizeof(g_list_mem)/sizeof(int); ++i) {
    test_mem.mem_write( Base+(4*i), g_list_mem[i] );
  }

  // test get
  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_get, Base+0,  0 ).data() );
  UTST_CHECK_EQ( 3, xcel_op( test_mem, opc_get, Base+12, 0 ).data() );
  UTST_CHECK_EQ( 4, xcel_op( test_mem, opc_get, Base+24, 0 ).data() );
  UTST_CHECK_EQ( 1, xcel_op( test_mem, opc_get, Base+36, 0 ).data() );
  UTST_CHECK_EQ( 2, xcel_op( test_mem, opc_get, Base+48, 0 ).data() );

  // test set
  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+0,  7 ).data() );
  UTST_CHECK_EQ( 7, xcel_op( test_mem, opc_get, Base+0,  0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+12, 4 ).data() );
  UTST_CHECK_EQ( 4, xcel_op( test_mem, opc_get, Base+12, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+24, 5 ).data() );
  UTST_CHECK_EQ( 5, xcel_op( test_mem, opc_get, Base+24, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+36, 9 ).data() );
  UTST_CHECK_EQ( 9, xcel_op( test_mem, opc_get, Base+36, 0 ).data() );

  UTST_CHECK_EQ( 0, xcel_op( test_mem, opc_set, Base+48, 8 ).data() );
  UTST_CHECK_EQ( 8, xcel_op( test_mem, opc_get, Base+48, 0 ).data() );
}

//-----------------------------------------------------------------------
// TestIncrDecr
//-----------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestIncrDecr )
{
  const unsigned Base = 1000;

  // create and load test memory
  TestMem test_mem;
  for (unsigned i = 0;i < sizeof(g_list_mem)/sizeof(int); ++i) {
    test_mem.mem_write( Base+(4*i), g_list_mem[i] );
  }

  // test incr
  UTST_CHECK_EQ( 36, xcel_op( test_mem, opc_incr, Base+0,  0).addr() );
  UTST_CHECK_EQ( 48, xcel_op( test_mem, opc_incr, Base+36, 0).addr() );
  UTST_CHECK_EQ( 12, xcel_op( test_mem, opc_incr, Base+48, 0).addr() );
  UTST_CHECK_EQ( 24, xcel_op( test_mem, opc_incr, Base+12, 0).addr() );

  // test incr
  UTST_CHECK_EQ( 12, xcel_op( test_mem, opc_decr, Base+24, 0).addr() );
  UTST_CHECK_EQ( 48, xcel_op( test_mem, opc_decr, Base+12, 0).addr() );
  UTST_CHECK_EQ( 36, xcel_op( test_mem, opc_decr, Base+48, 0).addr() );
  UTST_CHECK_EQ(  0, xcel_op( test_mem, opc_decr, Base+36, 0).addr() );
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
  list_node_ptr ptr( Base, 0, test_mem, test_mem );
  ptr->m_prev = Base;
  ptr->m_next = Base;
  ptr->m_value = 0;

  UTST_CHECK_EQ( Base+36, xcel_insert( test_mem,  Base+0, Base+36, 1 ).addr() );
  UTST_CHECK_EQ( Base+48, xcel_insert( test_mem, Base+36, Base+48, 2 ).addr() );
  UTST_CHECK_EQ( Base+12, xcel_insert( test_mem, Base+48, Base+12, 3 ).addr() );
  UTST_CHECK_EQ( Base+24, xcel_insert( test_mem, Base+12, Base+24, 4 ).addr() );

  // value ref
  int value_ref[4] = {4,3,2,1};

  // check memory by iterating through the list
  List::iterator::pointer p( Base, 0, test_mem, test_mem );
  List::iterator first( p );
  first++;
  // get iterator to end, which is header
  List::iterator last( p );
  int i = 0;
  for (; first != last; ++first) {
    int node_data = *first;
    UTST_CHECK_EQ( node_data, value_ref[i++] );
  }
}

//-----------------------------------------------------------------------
// TestInsertMemoization
//-----------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestInsertMemoization )
{
  const unsigned Base = 1000;

  // create and load test memory
  // here we just create a single element list, which is
  // a node with prev and next pointing to itself
  TestMem test_mem;
  list_node_ptr ptr( Base, 0, test_mem, test_mem );
  ptr->m_prev = Base;
  ptr->m_next = Base;
  ptr->m_value = 0;

  test_mem.clear_num_requests();

  // do 1 insert
  UTST_CHECK_EQ( Base+36, xcel_insert( test_mem,  Base+0, Base+36, 1 ).addr() );

  int n_loads  = test_mem.get_num_loads();
  int n_stores = test_mem.get_num_stores();
  
  printf ("----------------\n");
  printf ("loads:  %d\n", n_loads);
  printf ("stores: %d\n", n_stores);
  printf ("----------------\n");

  // 3 loads and 5 stores without memoization
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_list" );
}
