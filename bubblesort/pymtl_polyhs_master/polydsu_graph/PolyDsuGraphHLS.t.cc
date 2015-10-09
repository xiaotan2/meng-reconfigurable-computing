#include "utst/utst.h"
#include "polydsu_graph/PolyDsuGraphHLS.h"

using namespace xmem;
using namespace polydsu;

typedef _Graph<int> Graph;

// Global Constants
const unsigned opc_get  = PolyDsuReqMsg::TYPE_GET;
const unsigned opc_set  = PolyDsuReqMsg::TYPE_SET;
const unsigned opc_incr = PolyDsuReqMsg::TYPE_INCR;
const unsigned opc_decr = PolyDsuReqMsg::TYPE_DECR;
const unsigned opc_mfx  = PolyDsuReqMsg::TYPE_MFX;
const unsigned opc_mtx  = PolyDsuReqMsg::TYPE_MTX;

// Global test vector
const unsigned VBase = 100;
const unsigned EBase = VBase + 132;
const int g_graph_mem[] = {
    0,    0,    212,  116,          // 0, vertices header
    0,    0,    100,  132,          // 16 source
    0,    1,    116,  148,          // 32
    0,    2,    132,  164,          // 48
    0,    3,    148,  180,          // 64
    0,    4,    164,  196,          // 80
    0,    5,    180,  212,          // 96
    0,    6,    196,  100,          // 112
    0,                              // 128
    0,    0,    0,    252,  392,    // 132 edges header
    116,  132,  1,    272,  232,    // 152
    116,  148,  2,    292,  252,    // 172
    132,  164,  2,    312,  272,    // 192
    132,  180,  3,    332,  292,    // 212
    148,  180,  1,    352,  312,    // 232
    148,  196,  2,    372,  332,    // 252
    180,  212,  0,    392,  352,    // 272
    196,  212,  1,    232,  372,    // 292
};

//-----------------------------------------------------------------------
// Performs a single sssp computation
//-----------------------------------------------------------------------
PolyDsuRespMsg xcel_sssp(
    TestMem& test_mem,
    const unsigned v_header,     // tree header node
    const unsigned e_header,     // new node
    const unsigned src
){
  // Processor configuration streams
  hls::stream<PolyDsuReqMsg>   xcelreq;
  hls::stream<PolyDsuRespMsg>  xcelresp;

  // write requests to xcelreq
  //                           id opq  opc    raddr       data
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  1, v_header ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  2, e_header ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mtx,  3,      src ) );
  xcelreq.write( PolyDsuReqMsg( 0,  0, opc_mfx,  0,        0 ) );

  PolyDsuGraphHLS( xcelreq, xcelresp, test_mem, test_mem );

  xcelresp.read();
  xcelresp.read();
  xcelresp.read();
  return xcelresp.read();
}

//-----------------------------------------------------------------------
// TestSSSP
//-----------------------------------------------------------------------
// We build the test_mem list from a single node
UTST_AUTO_TEST_CASE( TestSSSP )
{
  // create and load test memory
  TestMem test_mem;
  for (unsigned i = 0; i < sizeof(g_graph_mem)/sizeof(int); ++i) {
    test_mem.mem_write( VBase+4*i, g_graph_mem[i] );
  }

  /*printf ("Mem before\n");
  for (unsigned i = 0; i < sizeof(g_graph_mem)/sizeof(int); ++i) {
    int data = test_mem.mem_read( VBase+4*i );
    printf ("%4d: %4d\n", VBase+4*i, data); 
  }*/

  Graph g( VBase, VBase+132, 0, test_mem, test_mem );

  UTST_CHECK_EQ( 1, xcel_sssp( test_mem, VBase, VBase+132, VBase+16 ).data() );

  /*printf ("Mem after\n");
  for (unsigned i = 0; i < sizeof(g_graph_mem)/sizeof(int); ++i) {
    int data = test_mem.mem_read( VBase+4*i );
    printf ("%4d: %4d\n", VBase+4*i, data); 
  }*/

  int ref[7] = {0,1,2,3,3,4,3};
  
  // check memory by iterating through the list
  Graph::vertex_iterator first = g.begin_vertices();
  Graph::vertex_iterator last  = g.end_vertices();
  int i = 0;
  for (; first != last; ++first) {
    int label = g.get_label( first );
    int data  = g.get_data( first );
    UTST_CHECK_EQ( data,  i );
    UTST_CHECK_EQ( label, ref[i] );
    ++i;
  }
  UTST_CHECK_EQ( i, 7 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------
int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_graph" );
}

