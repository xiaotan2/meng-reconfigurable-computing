//========================================================================
// PolyHS bintree inline methods
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : July 19, 2015
// Project : Polymorphic Hardware Specialization

#include <memory>
#include <assert.h>

// Macros for the sake of more readable code
#define _NODE_PTR typename xmem::MemValue< _Node<_Value> >::NodePointer
#define _NODE_PTR_PROXY xmem::MemValue< xmem::MemPointer< _Node<_Value> > >

//------------------------------------------------------------------------
// Memory Allocation/Deallocation
//------------------------------------------------------------------------

template<class _Value>
typename BinTree<_Value>::NodePtr
BinTree<_Value>::m_create_header(
    xmem::Opaque opq,
    xmem::MemReqStream& memreq, xmem::MemRespStream& memresp
){
  xmem::Address mem = (xmem::Address)malloc( Node::size() );
  assert( mem != 0 );
  NodePtr node( mem, opq, memreq, memresp );
  return node;
}

template<class _Value>
typename BinTree<_Value>::NodePtr
BinTree<_Value>::m_create_node(const _Value& x) {
  xmem::Address mem = (xmem::Address)malloc( Node::size() );
  assert( mem != 0 );
  NodePtr node( mem, m_header.get_opq(),
                m_header.memreq(), m_header.memresp()
              );
  node->m_value = x;
  return node;
}

template<class _Value>
typename BinTree<_Value>::NodePtr
BinTree<_Value>::m_clone_node( NodePtr x ) {
  NodePtr tmp = m_create_node(x->m_value);
  tmp->m_left = 0;
  tmp->m_right = 0;
  return tmp;
}

template<class _Value>
void BinTree<_Value>::m_destroy_node( NodePtr p ) {
  free( p.get_addr() );
}

//------------------------------------------------------------------------
// Constructors
//------------------------------------------------------------------------
template<class _Value>
BinTree<_Value>::BinTree(
    xmem::Opaque opq,
    xmem::MemReqStream& memreq, xmem::MemRespStream& memresp
)
  : m_header( m_create_header( opq, memreq, memresp ) ),
    m_node_count(0)
{
  empty_initialize();
}

template<class _Value>
BinTree<_Value>::BinTree(
    xmem::Address header_addr, xmem::Opaque opq,
    xmem::MemReqStream& memreq, xmem::MemRespStream& memresp
)
  : m_header( NodePtr( header_addr, opq, memreq, memresp ) ),
    m_node_count(0)
{
  empty_initialize();
}

template<class _Value>
BinTree<_Value>::BinTree(const BinTree<_Value>& x)
  : m_header( m_create_header( 0, x.m_header.get_opq(), 
              x.m_header.memreq(), x.m_header.memresp() ) ),
    m_node_count(0)
{
  if (x.root() == 0)
    empty_initialize();
  else {
    // copy the other tree
  }
  m_node_count = x.m_node_count;
}

//------------------------------------------------------------------------
// Destructors
//------------------------------------------------------------------------
template<class _Value>
BinTree<_Value>::~BinTree() {
  clear();
}

//------------------------------------------------------------------------
// Operators
//------------------------------------------------------------------------
template<class _Value>
BinTree<_Value>&
BinTree<_Value>::operator=( const BinTree<_Value>& x ) {
  if( this != &x ) {
    clear();
  }
  return *this;
}

//------------------------------------------------------------------------
// Private Helper Functions
//------------------------------------------------------------------------
// m_insert_left
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::m_insert_left( NodePtr x, NodePtr new_node ) {
  // insert the node between x and its left child
  x->m_left = new_node;
  new_node->m_parent = x;

  ++m_node_count;
}

//------------------------------------------------------------------------
// m_insert_right
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::m_insert_right( NodePtr x, NodePtr new_node ) {
  // insert the node between x and its right child
  x->m_right = new_node;
  new_node->m_parent = x;

  ++m_node_count;
}

//------------------------------------------------------------------------
// m_copy
//------------------------------------------------------------------------
template<class _Value>
typename BinTree<_Value>::NodePtr
BinTree<_Value>::m_copy( NodePtr x ) {
  // structural copy.  x and p must be non-null.
  // use m_clone node
}

//------------------------------------------------------------------------
// m_erase
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::m_erase( NodePtr x ) {
  // TODO: Make this non-recursive
  --m_node_count;
}

//------------------------------------------------------------------------
// empty_initialize
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::empty_initialize() {
  m_header->m_parent = 0;
  m_header->m_left  = 0;
  m_header->m_right = 0;
}

//------------------------------------------------------------------------
// Preorder Iterator Methods
//------------------------------------------------------------------------
template<class _Value>
typename BinTree<_Value>::preorder_iterator
BinTree<_Value>::begin_preorder() {
  // the first preorder node is the root
  return preorder_iterator(root());
}

template<class _Value>
typename BinTree<_Value>::preorder_iterator
BinTree<_Value>::end_preorder() {
  return preorder_iterator( m_header );
}

//------------------------------------------------------------------------
// Inorder Iterator Methods
//------------------------------------------------------------------------
template<class _Value>
typename BinTree<_Value>::inorder_iterator
BinTree<_Value>::begin_inorder() {
  // the first inorder node is the furthest left in the tree
  NodePtr curr = root();
  if (curr != 0) {
    while (curr->m_left != 0)
      curr = curr->m_left;
  }
  return inorder_iterator(curr);
}

template<class _Value>
typename BinTree<_Value>::inorder_iterator
BinTree<_Value>::end_inorder() {
  return inorder_iterator( m_header );
}

//------------------------------------------------------------------------
// set root
//------------------------------------------------------------------------

template<class _Value>
typename BinTree<_Value>::iterator
BinTree<_Value>::set_root( const _Value& v ) {
  NodePtr node = m_create_node( v );
  return set_root( node );
}

template<class _Value>
typename BinTree<_Value>::iterator
BinTree<_Value>::set_root( NodePtr node ) {
  m_header->m_left = m_header->m_right = node;
  node->m_parent = m_header;
  m_node_count++;
  return iterator( node );
}

//------------------------------------------------------------------------
// insert
//------------------------------------------------------------------------

template<class _Value> 
template<class iter>
iter BinTree<_Value>::insert_left(iter pos, const _Value& v) {
  NodePtr node = m_create_node( v );
  return insert_left( pos, node );
}

template<class _Value> 
template<class iter>
iter BinTree<_Value>::insert_right(iter pos, const _Value& v) {
  NodePtr node = m_create_node( v );
  return insert_right( pos, node );
}

template<class _Value> 
template<class iter>
iter BinTree<_Value>::insert_left(iter pos, NodePtr node) {
  m_insert_left( pos.m_node, node );
  return iter( node );
}

template<class _Value> 
template<class iter>
iter BinTree<_Value>::insert_right(iter pos, NodePtr node) {
  m_insert_right( pos.m_node, node );
  return iter( node );
}

//------------------------------------------------------------------------
// erase
//------------------------------------------------------------------------
template<class _Value>
template<class iter>
void BinTree<_Value>::erase( iter pos ) {
  m_erase( pos.m_node );
}

//------------------------------------------------------------------------
// clear
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::clear() {
  m_erase( root() );
  m_header->m_left = m_header->m_right = 0;
}

//------------------------------------------------------------------------
// find
//------------------------------------------------------------------------
template<class _Value>
template<class iter>
iter BinTree<_Value>::find(const _Value& x) const
{
  return iter( root() );
}

//------------------------------------------------------------------------
// count
//------------------------------------------------------------------------
template<class _Value>
typename BinTree<_Value>::size_type
BinTree<_Value>::count(const _Value& x) const
{
  return 0;
}

//------------------------------------------------------------------------
// _dump_node and _dump_tree
//------------------------------------------------------------------------
template<class _Value>
void BinTree<_Value>::_dump_node( const NodePtr node,
                           const std::string prefix,
                           const char lr ) {
  if (node == 0) {
    printf ("%s%c\n", prefix.c_str(), lr);
    return;
  }
  printf ("%s%c:(%3d,%3d)\n", prefix.c_str(), lr,
      (_Value)node->m_value
    );
}

template<class _Value>
void BinTree<_Value>::_dump_subtree( const NodePtr node,
                              const std::string prefix,
                              const char lr ) {
  _dump_node( node, prefix, lr );
  if (node->m_left != 0)
    _dump_subtree( node->m_left,  prefix+"  ", 'L' );
  if (node->m_right != 0)
    _dump_subtree( node->m_right, prefix+"  ", 'R' );
}

template<class _Value>
void BinTree<_Value>::_dump_tree() const {
  _dump_subtree( root() );
}

//------------------------------------------------------------------------
// BinTreeIterator increment
//------------------------------------------------------------------------
/*void BinTreeIterator<_Value,_VProxy,NodePtr>::_increment() {
  if( m_node->m_right != 0 ) {
    m_node = m_node->m_right;
    while( m_node->m_left != 0 ) {
      m_node = m_node->m_left;
    }
  }
  else {
    NodePtr y = m_node->m_parent;
    while( m_node == y->m_right ) {
      m_node = y;
      y = y->m_parent;
    }
    if( m_node->m_right != y )
      m_node = y;
  }
}*/

//------------------------------------------------------------------------
// BinTreeIterator decrement
//------------------------------------------------------------------------
/*template<class _Value,
         class _VProxy, class NodePtr>
void BinTreeIterator<_Value,_VProxy,NodePtr>::_decrement() {
  if( m_node->m_color == s_BinTreeRed && (*(m_node->m_parent)).m_parent == m_node) {
    m_node = m_node->m_right;
  }
  else if( m_node-> m_left != 0 ) {
    NodePtr y = m_node->m_left;
    while( y->m_right != 0 )
      y = y->m_right;
    m_node = y;
  }
  else {
    NodePtr y = m_node->m_parent;
    while( m_node == y->m_left ) {
      m_node = y;
      y = y->m_parent;
    }
    m_node = y;
  }
}*/

//------------------------------------------------------------------------
// Tree rotation and recoloring using the base node pointers
// Note these were inline in the original stl impl.
//------------------------------------------------------------------------
// Rotate Left
//------------------------------------------------------------------------
template<typename _Value>
void _BinTreeRotateLeft( _NODE_PTR x, _NODE_PTR_PROXY& root ) {
  _NODE_PTR y = x->m_right;
  x->m_right = y->m_left;
  if( y->m_left != 0 )
    y->m_left->m_parent = x;
  y->m_parent = x->m_parent;

  if (x == root)
    root = y;
  else if (x == x->m_parent->m_left)
    x->m_parent->m_left = y;
  else
    x->m_parent->m_right = y;
  y->m_left = x;
  x->m_parent = y;
}

//------------------------------------------------------------------------
// Rotate Right
//------------------------------------------------------------------------
template<typename _Value>
void _BinTreeRotateRight( _NODE_PTR x, _NODE_PTR_PROXY& root ) {
  _NODE_PTR y = x->m_left;
  x->m_left = y->m_right;
  if (y->m_right != 0)
    y->m_right->m_parent = x;
  y->m_parent = x->m_parent;

  if (x == root)
    root = y;
  else if (x == x->m_parent->m_right)
    x->m_parent->m_right = y;
  else
    x->m_parent->m_left = y;
  y->m_right = x;
  x->m_parent = y;
}

#undef _NODE_PTR
#undef _NODE_PTR_PROXY
