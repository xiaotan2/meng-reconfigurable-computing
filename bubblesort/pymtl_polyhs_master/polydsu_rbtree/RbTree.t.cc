//========================================================================
// RbTree.t.cc
//========================================================================

#include "utst/utst.h"
#include "polydsu_rbtree/RbTree.h"

using namespace xmem;

typedef RbTree<int,int> Tree;

//--------------------------------------------------------------
// Test Insert and Iterator
//--------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestSimple )
{
  TestMem test_mem;

  // set up tree header
  Tree::NodePtr header( 100, 0, test_mem, test_mem );
  header->m_parent  = 0;            // Null
  header->m_color   = s_RbTreeRed;
  header->m_left    = header;
  header->m_right   = header;

  Tree t( header );
  t.insert_unique( 148, 3, 3 ); 
  t.insert_unique( 172, 2, 2 );
  t.insert_unique( 220, 5, 5 );
  t.insert_unique( 124, 1, 1 ); 
  t.insert_unique( 196, 4, 4 );
  t.insert_unique( 244, 0, 0 );
  UTST_CHECK_EQ( t.size(), 6u );

  int ref[] = {0,1,2,3,4,5};

  Tree::iterator first  = t.begin();
  Tree::iterator last   = t.end();
  int i = 0;
  for (; first != last; ++first) {
    UTST_CHECK( *first == ref[i++] );
  }
  UTST_CHECK_EQ( i, static_cast<int>(t.size()) );
}

//--------------------------------------------------------------
// Test FindIterator
//--------------------------------------------------------------
UTST_AUTO_TEST_CASE( TestFind )
{
  TestMem test_mem;
  int N = 1000;

  // set up tree header
  Tree::NodePtr header( 100, 0, test_mem, test_mem );
  header->m_parent  = 0;            // Null
  header->m_color   = s_RbTreeRed;
  header->m_left    = header;
  header->m_right   = header;

  Tree t( header );
  for (int i = 1; i <= N; ++i) { 
    t.insert_unique( 100 + 4*6*i, i, i );
  }
  UTST_CHECK_EQ( t.size(), static_cast<unsigned>(N) );

  // successful find
  for (int i = 1; i <= N; ++i) {
    Tree::find_iterator it   = t.begin_find( i );
    Tree::find_iterator last = t.end_find( i );
    int counter = 0;
    while (it != last) {
      ++it;
      ++counter;
    }

    UTST_CHECK_EQ ( it.found(), true );
    UTST_CHECK_EQ ( it.key(), i );
    UTST_CHECK ( counter < 40 );
  }

  // unsuccessful find
  int nofind[] = {-2,-1,0,N+1,N+2,N+3};
  for (int i = 0; i < (int)(sizeof(nofind)/sizeof(int)); ++i) {
    Tree::find_iterator it   = t.begin_find( nofind[i] );
    Tree::find_iterator last = t.end_find( nofind[i] );
    int counter = 0;
    while (it != last) {
      ++it;
      ++counter;
    }

    UTST_CHECK_EQ ( it.found(), false );
    UTST_CHECK ( counter < 40 );
  }
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "rbtree" );
}

