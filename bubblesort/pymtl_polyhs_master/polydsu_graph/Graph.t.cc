//========================================================================
// Graph implementation unit tests
//========================================================================
// Note this only tests iterator functionality (begin, end, ++iter)
// and selected morph operations (insert, erase). These are needed
// to build the accelerator

#include "utst/utst.h"
#include "polydsu_graph/Graph.h"
#include <stdio.h>
#include <assert.h>

using namespace xmem;

typedef _Graph<int> Graph;

//------------------------------------------------------------------------
// Test Graph
//------------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestVertexAndEdge )
{
  TestMem test_mem;
  Graph g( 0x100, 0x200, 0, test_mem, test_mem );
  
  // initialize Vertices
  Graph::VertexPtr v( 0x100, 0, test_mem, test_mem );
  v->m_prev = v->m_next = v;
  
  Graph::VertexPtr v1( 0x110, 0, test_mem, test_mem );
  v1->m_label = 1;
  v1->m_data = 1;
  Graph::VertexPtr v2( 0x120, 0, test_mem, test_mem );
  v2->m_label = 2;
  v2->m_data = 2;
  Graph::VertexPtr v3( 0x130, 0, test_mem, test_mem );
  v3->m_label = 3;
  v3->m_data = 3;

  // Add each vertex to the graph
  Graph::vertex_iterator vi1 = g.add_vertex( v1 );
  Graph::vertex_iterator vi2 = g.add_vertex( v2 );
  Graph::vertex_iterator vi3 = g.add_vertex( v3 );
  
  // test vertices
  UTST_CHECK_EQ( g.num_vertices(), 3u );
  Graph::vertex_iterator first = g.begin_vertices();
  Graph::vertex_iterator last  = g.end_vertices();
  int i = 0;
  for (; first != last; ++first) {
    ++i;
    UTST_CHECK_EQ( g.get_data(first), i );
    UTST_CHECK_EQ( g.get_label(first), i );
  }
  UTST_CHECK_EQ( i, 3 );

  // initialize Edges
  Graph::EdgePtr e( 0x200, 0, test_mem, test_mem );
  e->m_prev = e->m_next = e;
  Graph::EdgePtr e1( 0x220, 0, test_mem, test_mem );
  e1->src = v1;
  e1->dst = v2;
  e1->m_weight = 1;
  Graph::EdgePtr e2( 0x240, 0, test_mem, test_mem );
  e2->src = v2;
  e2->dst = v3;
  e2->m_weight = 2;
  Graph::EdgePtr e3( 0x260, 0, test_mem, test_mem );
  e3->src = v3;
  e3->dst = v1;
  e3->m_weight = 3;

  // Add edges to the graph
  Graph::edge_iterator ei1 = g.add_edge( e1 );
  Graph::edge_iterator ei2 = g.add_edge( e2 );
  Graph::edge_iterator ei3 = g.add_edge( e3 );

  // test edges
  UTST_CHECK_EQ( g.num_edges(), 3u );
  Graph::edge_iterator first1 = g.begin_edges();
  Graph::edge_iterator last1  = g.end_edges();
  i = 0;
  for (; first1 != last1; ++first1) {
    ++i;
    UTST_CHECK_EQ( g.get_weight(first1), i );
  }
  UTST_CHECK_EQ( i, 3 );
  UTST_CHECK( g.get_src(e1) == vi1 );
  UTST_CHECK( g.get_dst(e1) == vi2 );
  UTST_CHECK( g.get_src(e2) == vi2 );
  UTST_CHECK( g.get_dst(e2) == vi3 );
  UTST_CHECK( g.get_src(e3) == vi3 );
  UTST_CHECK( g.get_dst(e3) == vi1 );

}

//------------------------------------------------------------------------
// Test SSSP
//------------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestSSSP )
{
  const unsigned VBase = 100;
  const unsigned EBase = 232;

  TestMem test_mem;
  for (int i = 0; i < 1000; ++i) {
    test_mem.mem_write( 100+4*i, -1 );
  }
  Graph g( VBase, EBase, 0, test_mem, test_mem );
  
  // initialize VertexList
  Graph::VertexPtr v(  VBase, 0, test_mem, test_mem );
  v->m_prev = v->m_next = v;
  // Vertices
  Graph::VertexPtr v0( VBase+16, 0, test_mem, test_mem );
  v0->m_data = 0;
  Graph::VertexPtr v1( VBase+32, 0, test_mem, test_mem );
  v1->m_data = 1;
  Graph::VertexPtr v2( VBase+48, 0, test_mem, test_mem );
  v2->m_data = 2;
  Graph::VertexPtr v3( VBase+64, 0, test_mem, test_mem );
  v3->m_data = 3;
  Graph::VertexPtr v4( VBase+80, 0, test_mem, test_mem );
  v4->m_data = 4;
  Graph::VertexPtr v5( VBase+96, 0, test_mem, test_mem );
  v5->m_data = 5;
  Graph::VertexPtr v6( VBase+112, 0, test_mem, test_mem );
  v6->m_data = 6;

  // Add each vertex to the graph
  Graph::vertex_iterator vi0 = g.add_vertex( v0 );
  Graph::vertex_iterator vi1 = g.add_vertex( v1 );
  Graph::vertex_iterator vi2 = g.add_vertex( v2 );
  Graph::vertex_iterator vi3 = g.add_vertex( v3 );
  Graph::vertex_iterator vi4 = g.add_vertex( v4 );
  Graph::vertex_iterator vi5 = g.add_vertex( v5 );
  Graph::vertex_iterator vi6 = g.add_vertex( v6 );
  
  // initialize EdgeList
  Graph::EdgePtr e( EBase, 0, test_mem, test_mem );
  e->m_prev = e->m_next = e;
  // Edges
  Graph::EdgePtr e0( EBase+20, 0, test_mem, test_mem );
  e0->src = v0;
  e0->dst = v1;
  e0->m_weight = 1;
  Graph::EdgePtr e1( EBase+40, 0, test_mem, test_mem );
  e1->src = v0;
  e1->dst = v2;
  e1->m_weight = 2;
  Graph::EdgePtr e2( EBase+60, 0, test_mem, test_mem );
  e2->src = v1;
  e2->dst = v3;
  e2->m_weight = 2;
  Graph::EdgePtr e3( EBase+80, 0, test_mem, test_mem );
  e3->src = v1;
  e3->dst = v4;
  e3->m_weight = 3;
  Graph::EdgePtr e4( EBase+100, 0, test_mem, test_mem );
  e4->src = v2;
  e4->dst = v4;
  e4->m_weight = 1;
  Graph::EdgePtr e5( EBase+120, 0, test_mem, test_mem );
  e5->src = v2;
  e5->dst = v5;
  e5->m_weight = 2;
  Graph::EdgePtr e6( EBase+140, 0, test_mem, test_mem );
  e6->src = v4;
  e6->dst = v6;
  e6->m_weight = 0;
  Graph::EdgePtr e7( EBase+160, 0, test_mem, test_mem );
  e7->src = v5;
  e7->dst = v6;
  e7->m_weight = 1;

  // Add edges to the graph
  Graph::edge_iterator ei0 = g.add_edge( e0 );
  Graph::edge_iterator ei1 = g.add_edge( e1 );
  Graph::edge_iterator ei2 = g.add_edge( e2 );
  Graph::edge_iterator ei3 = g.add_edge( e3 );
  Graph::edge_iterator ei4 = g.add_edge( e4 );
  Graph::edge_iterator ei5 = g.add_edge( e5 );
  Graph::edge_iterator ei6 = g.add_edge( e6 );
  Graph::edge_iterator ei7 = g.add_edge( e7 );

  bool success = g.bellman_ford( v0 );
  UTST_CHECK( success );

  int ref[7] = {0,1,2,3,3,4,3};

  for (Graph::vertex_iterator v = g.begin_vertices(), ve = g.end_vertices();
       v != ve; ++v)
  {
    UTST_CHECK_EQ( ref[g.get_data(v)], (int)g.get_label(v) );
  }

  // dump memory
  /*printf ("Vertices:\n");
  for (int i = 0; i < 34; ++i) {
    int addr = VBase + i*4;
    printf ("%3d: %3d\n", addr, test_mem.mem_read(addr) );
  }
  printf ("Edges:\n");
  for (int i = 0; i < 48; ++i) {
    int addr = EBase + i*4;
    printf ("%3d: %3d\n", addr, test_mem.mem_read(addr) );
  }*/
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_graph" );
}
