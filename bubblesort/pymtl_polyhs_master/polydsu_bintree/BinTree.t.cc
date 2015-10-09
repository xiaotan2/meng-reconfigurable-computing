//========================================================================
// PolyHS BinTree implementation unit tests
//========================================================================
// Note this only tests iterator functionality (begin, end, ++iter)
// and selected morph operations (insert, erase). These are needed
// to build the accelerator

#include "utst/utst.h"
#include "polydsu_bintree/BinTree.h"
#include <stdio.h>
#include <assert.h>

using namespace xmem;

typedef int Value;

//------------------------------------------------------------------------
// Test InorderIter
//------------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestInorderIter )
{
  /* create simple tree
   *     3
   *   /   \
   *  1     5
   *   \   / \
   *    2 4   6
  */

  // first create the nodes
  TestMem test_mem;
  BinTree<Value>::NodePtr n1( 0x20, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n2( 0x30, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n3( 0x40, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n4( 0x50, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n5( 0x60, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n6( 0x70, 0, test_mem, test_mem );

  n1->m_value = 1;
  n2->m_value = 2;
  n3->m_value = 3;
  n4->m_value = 4;
  n5->m_value = 5;
  n6->m_value = 6;

  // setup the tree
  BinTree<Value> tree( 0x10, 0, test_mem, test_mem );
  tree.set_root( n3 );

  BinTree<Value>::preorder_iterator it3 = tree.begin_preorder();
  BinTree<Value>::preorder_iterator it1 = tree.insert_left ( it3, n1 );
  BinTree<Value>::preorder_iterator it2 = tree.insert_right( it1, n2 );
  BinTree<Value>::preorder_iterator it5 = tree.insert_right( it3, n5 );
  BinTree<Value>::preorder_iterator it4 = tree.insert_left ( it5, n4 );
  BinTree<Value>::preorder_iterator it6 = tree.insert_right( it5, n6 );
  
  // dump the memory
  /*for (int i = 0; i < 32; ++i) {
    int addr = i*4;
    printf ("%3d: %3d\n", addr, test_mem.mem_read(addr) );
  }*/

  test_mem.clear_num_requests();

  // test forward iteration, also set at each iter
  BinTree<Value>::inorder_iterator first = tree.begin_inorder();
  UTST_CHECK( first == it1 );
  UTST_CHECK_EQ( *first, 1 );
  *first = 6;
  ++first;
  UTST_CHECK( first == it2 );
  UTST_CHECK_EQ( *first, 2 );
  *first = 5;
  ++first;
  UTST_CHECK( first == it3 );
  UTST_CHECK_EQ( *first, 3 );
  *first = 4;
  ++first;
  UTST_CHECK( first == it4 );
  UTST_CHECK_EQ( *first, 4 );
  *first = 3;
  ++first;
  UTST_CHECK( first == it5 );
  UTST_CHECK_EQ( *first, 5 );
  *first = 2;
  ++first;
  UTST_CHECK( first == it6 );
  UTST_CHECK_EQ( *first, 6 );
  *first = 1;
  ++first;
  UTST_CHECK( first == tree.end_inorder() );

  int num_loads   = test_mem.get_num_loads();
  int num_stores  = test_mem.get_num_stores();
  printf ("----------------------------------\n");
  printf ("avg loads : %4.2f\n", (float)num_loads/6);
  printf ("avg stores: %4.2f\n", (float)num_stores/6);
  printf ("----------------------------------\n");


  // test reverse iteration, get at each iter
  BinTree<Value>::inorder_iterator last = tree.end_inorder();
  --last;
  UTST_CHECK( last == it6 );
  UTST_CHECK_EQ( *last, 1 );
  --last;
  UTST_CHECK( last == it5 );
  UTST_CHECK_EQ( *last, 2 );
  --last;
  UTST_CHECK( last == it4 );
  UTST_CHECK_EQ( *last, 3 );
  --last;
  UTST_CHECK( last == it3 );
  UTST_CHECK_EQ( *last, 4 );
  --last;
  UTST_CHECK( last == it2 );
  UTST_CHECK_EQ( *last, 5 );
  --last;
  UTST_CHECK( last == it1 );
  UTST_CHECK_EQ( *last, 6 );
}

//------------------------------------------------------------------------
// Test PreorderIter
//------------------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestPreorderIter )
{
  /* create simple tree
   *      1
   *    /   \
   *   2     4
   *  /     / \
   * 3     5   7
   *        \
   *         6
  */
  // first create the nodes
  TestMem test_mem;
  BinTree<Value>::NodePtr n1( 0x20, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n2( 0x30, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n3( 0x40, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n4( 0x50, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n5( 0x60, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n6( 0x70, 0, test_mem, test_mem );
  BinTree<Value>::NodePtr n7( 0x80, 0, test_mem, test_mem );

  n1->m_value = 1;
  n2->m_value = 2;
  n3->m_value = 3;
  n4->m_value = 4;
  n5->m_value = 5;
  n6->m_value = 6;
  n7->m_value = 6;

  // setup the tree
  BinTree<Value> tree( 0x10, 0, test_mem, test_mem );
  tree.set_root( n1 );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu_bintree" );
}
