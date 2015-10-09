//========================================================================
// PolyHS rbtree inline methods
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : July 19, 2015
// Project : Polymorphic Hardware Specialization
//
// rbtree inspired from C++ STL.

#include <memory>
#include <assert.h>

#include "polydsu_rbtree/RbTree.h"

//------------------------------------------------------------------------
// Memory Allocation/Deallocation
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::NodePtr
RbTree<_Key,_Value>::m_create_node(
    xmem::Address mem,
    const _Key& k, const _Value& x
){
  NodePtr node( mem, m_header.get_opq(), 
                m_header.memreq(), m_header.memresp() );
  node->m_key = k;
  node->m_value = x;
  return node;
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::NodePtr
RbTree<_Key,_Value>::m_clone_node( NodePtr x ) {
  NodePtr tmp = m_create_node(x->m_key, x->m_value);
  tmp->m_color = x->m_color;
  tmp->m_left = 0;
  tmp->m_right = 0;
  return tmp;
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::m_destroy_node( NodePtr p ) {
}

//------------------------------------------------------------------------
// Constructors
//------------------------------------------------------------------------
template<class _Key, class _Value>
RbTree<_Key,_Value>::RbTree(
    xmem::Address mem, xmem::Opaque opq,
    xmem::MemReqStream& memreq, xmem::MemRespStream& memresp
)
  : m_header( mem, opq, memreq, memresp ),
    m_node_count(0)
{
  empty_initialize();
}

template<class _Key, class _Value>
RbTree<_Key,_Value>::RbTree( NodePtr header )
  : m_header( header ),
    m_node_count(0)
{
}

//------------------------------------------------------------------------
// Destructors
//------------------------------------------------------------------------
template<class _Key, class _Value>
RbTree<_Key,_Value>::~RbTree() {
}

//------------------------------------------------------------------------
// Private Helper Functions
//------------------------------------------------------------------------
// m_insert
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::iterator
RbTree<_Key,_Value>::m_insert(
    xmem::Address mem,
    NodePtr x_, NodePtr y_,
    const _Key& k, const _Value& v
){
  NodePtr x = (NodePtr) x_;
  NodePtr y = (NodePtr) y_;
  NodePtr z = m_create_node( mem, k, v );

  if (y == m_header || x != 0 ||
      (k < s_key(y))) {
    s_left(y) = z;               // also makes m_header->m_left = z
                                      //    when y == m_header
    if (y == m_header) {
      m_header->m_parent = z;
      m_header->m_right = z;
    }
    else if (y == m_header->m_left)
      m_header->m_left = z;   // maintain m_header->m_left pointing to min node
  }
  else {
    s_right(y) = z;
    if (y == m_header->m_right)
      m_header->m_right = z;  // maintain m_header->m_right pointing to max node
  }
  s_parent(z) = y;
  s_left(z) = 0;
  s_right(z) = 0;
  _RbTreeRebalance(z, m_header->m_parent);
  ++m_node_count;
  return iterator(z);
}

//------------------------------------------------------------------------
// m_copy
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::NodePtr
RbTree<_Key,_Value>::m_copy( NodePtr x, NodePtr p ) {
  // structural copy.  x and p must be non-null.
  NodePtr top = m_clone_node(x);
  top->m_parent = p;

  if (x->m_right != 0)
    top->m_right = m_copy(s_right(x), top);
  p = top;
  x = s_left(x);

  while (x != 0) {
    NodePtr y = m_clone_node(x);
    p->m_left = y;
    y->m_parent = p;
    if (x->m_right != 0)
      y->m_right = m_copy(s_right(x), y);
    p = y;
    x = s_left(x);
  }

  return top;
}

//------------------------------------------------------------------------
// m_erase
//------------------------------------------------------------------------
template<class _Key, class _Value>
void RbTree<_Key,_Value>::m_erase( NodePtr x ) {
  // erase without rebalancing
  while (x != 0) {
    m_erase(s_right(x));
    NodePtr y = s_left(x);
     m_destroy_node(x);
    x = y;
  }
}

//------------------------------------------------------------------------
// empty_initialize and clear
//------------------------------------------------------------------------
template<class _Key, class _Value>
void RbTree<_Key,_Value>::empty_initialize() {
  s_color(m_header) = s_RbTreeRed;  // used to distinguish header from
                                    // root, in iterator.operator++
  m_header->m_parent = 0;
  m_header->m_left = m_header;
  m_header->m_right = m_header;
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::clear() {
  if (m_node_count != 0) {
    m_erase(m_header->m_parent);
    m_header->m_left = m_header;
    m_header->m_parent = 0;
    m_header->m_right = m_header;
    m_node_count = 0;
  }
}

//------------------------------------------------------------------------
// insert_unique
//------------------------------------------------------------------------
template<class _Key, class _Value>
std::pair<typename RbTree<_Key,_Value>::iterator, bool>
RbTree<_Key,_Value>::insert_unique(
    xmem::Address mem,
    const _Key& _k, const _Value& _v
){
  NodePtr y = m_header;
  NodePtr x = m_header->m_parent;
  bool comp = true;
  while (x != 0) {
    y = x;
    comp = (_k < s_key(x));
    x = comp ? s_left(x) : s_right(x);
  }
  iterator j = iterator(y);
  bool empty_tree = false;
  if (comp) {
    if (j == begin())
      empty_tree = true;
    else
      --j;
  }
  if ( !empty_tree && !(s_key(j.m_node) < _k) )
    return std::pair<iterator,bool>(j, false);
  return std::pair<iterator,bool>(m_insert(mem, x, y, _k, _v), true);
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::iterator
RbTree<_Key,_Value>::insert_unique(
    iterator position,
    xmem::Address mem,
    const _Key& _k, const _Value& _v
){
  if (position.m_node == m_header->m_left) { // begin()
    if (size() > 0 && _k < s_key(position.m_node))
      return m_insert(mem, position.m_node, position.m_node, _k, _v);
    // first argument just needs to be non-null
    else
      return insert_unique(_k,_v).first;
  } else if (position.m_node == m_header) { // end()
    if (s_key(m_header->m_right) < _k)
      return m_insert(mem, 0, m_header->m_right, _k, _v);
    else
      return insert_unique(_k,_v).first;
  } else {
    iterator before = position;
    --before;
    if (s_key(before.m_node) < _k
        && _k < s_key(position.m_node)) {
      if (s_right(before.m_node) == 0)
        return m_insert(mem, 0, before.m_node, _k, _v);
      else
        return m_insert(mem, position.m_node, position.m_node, _k, _v);
    // first argument just needs to be non-null
    } else
      return insert_unique(_k,_v).first;
  }
}

/*template<class _Key, class _Value>
void RbTree<_Key,_Value>::insert_unique( const_iterator first, const_iterator last )
{
  for ( ; first != last; ++first)
    insert_unique(first.key(), *first);
}

  template<class _Key, class _Value>
void RbTree<_Key,_Value>::insert_unique( iterator first, iterator last )
{
  for ( ; first != last; ++first)
    insert_unique(first.key(), *first);
}*/

/*template<class _Key, class _Value>
void RbTree<_Key,_Value>::insert_unique( const _Value* first, const _Value* last )
{
  for ( ; first != last; ++first)
    insert_unique(*first);
}*/

//------------------------------------------------------------------------
// erase
//------------------------------------------------------------------------
template<class _Key, class _Value>
void RbTree<_Key,_Value>::erase( iterator position ) {
  NodePtr y =
    (NodePtr) _RbTreeRebalanceForErase(
                  position.m_node,
                  m_header->m_parent,
                  m_header->m_left,
                  m_header->m_right);
  m_destroy_node(y);
  --m_node_count;
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::size_type
RbTree<_Key,_Value>::erase( const _Key& x ) {
  std::pair<iterator,iterator> _p = equal_range(x);
  size_type _n = std::distance(_p.first, _p.second);
  erase(_p.first, _p.second);
  return _n;
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::erase( iterator first, iterator last ) {
  if (first == begin() && last == end())
    clear();
  else
    while (first != last) erase(first++);
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::erase( const _Key* first, const _Key* last ) {
  while (first != last) erase(*first++);
}

//------------------------------------------------------------------------
// find
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::iterator
RbTree<_Key,_Value>::find(const _Key& _k)
{
  NodePtr y = m_header;      // Last node which is not less than _k.
  NodePtr x = m_header->m_parent;      // Current node.

  while (x != 0)
    if (!(s_key(x) < _k))
      y = x, x = s_left(x);
    else
      x = s_right(x);

  iterator j = iterator(y);
  return (j == end() || (_k < s_key(j.m_node))) ?
     end() : j;
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::const_iterator
RbTree<_Key,_Value>::find(const _Key& _k) const
{
  NodePtr y = m_header; /* Last node which is not less than _k. */
  NodePtr x = m_header->m_parent; /* Current node. */

  while (x != 0) {
    if (!(s_key(x) < _k))
      y = x, x = s_left(x);
    else
      x = s_right(x);
  }
  const_iterator j = const_iterator(y);
  return (j == end() || (_k < s_key(j.m_node))) ?
    end() : j;
}

//------------------------------------------------------------------------
// count
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::size_type
RbTree<_Key,_Value>::count(const _Key& _k) const
{
  std::pair<const_iterator, const_iterator> p = equal_range(_k);
  size_type n = 0;
  std::distance(p.first, p.second, n);
  return n;
}

//------------------------------------------------------------------------
// lower_bound
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::iterator
RbTree<_Key,_Value>::lower_bound(const _Key& _k)
{
  NodePtr y = m_header; /* Last node which is not less than _k. */
  NodePtr x = m_header->m_parent; /* Current node. */

  while (x != 0)
    if (!(s_key(x) < _k))
      y = x, x = s_left(x);
    else
      x = s_right(x);

  return iterator(y);
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::const_iterator
RbTree<_Key,_Value>::lower_bound(const _Key& _k) const
{
  NodePtr y = m_header; /* Last node which is not less than _k. */
  NodePtr x = m_header->m_parent; /* Current node. */

  while (x != 0)
    if (!(s_key(x) < _k))
      y = x, x = s_left(x);
    else
      x = s_right(x);

  return const_iterator(y);
}

//------------------------------------------------------------------------
// upper_bound
//------------------------------------------------------------------------
template<class _Key, class _Value>
typename RbTree<_Key,_Value>::iterator
RbTree<_Key,_Value>::upper_bound(const _Key& _k)
{
  NodePtr y = m_header; /* Last node which is greater than _k. */
  NodePtr x = m_header->m_parent; /* Current node. */

   while (x != 0)
     if (_k < s_key(x))
       y = x, x = s_left(x);
     else
       x = s_right(x);

   return iterator(y);
}

template<class _Key, class _Value>
typename RbTree<_Key,_Value>::const_iterator
RbTree<_Key,_Value>::upper_bound(const _Key& _k) const
{
  NodePtr y = m_header; /* Last node which is greater than _k. */
  NodePtr x = m_header->m_parent; /* Current node. */

   while (x != 0)
     if (_k < s_key(x))
       y = x, x = s_left(x);
     else
       x = s_right(x);

   return const_iterator(y);
}

//------------------------------------------------------------------------
// Debugging
//------------------------------------------------------------------------
template<class _Key, class _Value>
int RbTree<_Key,_Value>::black_count(NodePtr node, NodePtr root) const
{
  if (node == 0)
    return 0;
  else {
    int bc = node->m_color == s_RbTreeBlack ? 1 : 0;
    if (node == root)
      return bc;
    else
      return bc + black_count(node->m_parent, root);
  }
}

template<class _Key, class _Value>
bool RbTree<_Key,_Value>::_rb_verify() const {
  if (m_node_count == 0 || begin() == end())
    return m_node_count == 0 && begin() == end() &&
      m_header->m_left == m_header && m_header->m_right == m_header;

  int len = black_count(m_header->m_left, m_header->m_parent);
  for (const_iterator __it = begin(); __it != end(); ++__it) {
    NodePtr x = (NodePtr) __it.m_node;
    NodePtr L = s_left(x);
    NodePtr R = s_right(x);

    if (x->m_color == s_RbTreeRed)
      if ((L && L->m_color == s_RbTreeRed) ||
          (R && R->m_color == s_RbTreeRed))
        return false;

    if (L && (s_key(x) < s_key(L)))
      return false;
    if (R && (s_key(R) < s_key(x)))
      return false;

    if (!L && !R && black_count(x, m_header->m_parent) != len)
      return false;
  }

  if (m_header->m_left != RbTree<_Key,_Value>::s_minimum(m_header->m_parent))
    return false;
  if (m_header->m_right != RbTree<_Key,_Value>::s_maximum(m_header->m_parent))
    return false;

  return true;
}

//------------------------------------------------------------------------
// _dump_node and _dump_tree
//------------------------------------------------------------------------
template<class _Key, class _Value>
void RbTree<_Key,_Value>::_dump_node( const NodePtr node,
                           const std::string prefix,
                           const char lr ) {
  if (node == 0) {
    printf ("%s%c\n", prefix.c_str(), lr);
    return;
  }
  printf ("%s%c:(%3d,%3d):%s\n", prefix.c_str(), lr,
      (_Value)node->m_key, (_Value)node->m_value,
      ((ColorType)node->m_color ? "blk" : "red")
    );
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::_dump_subtree( const NodePtr node,
                              const std::string prefix,
                              const char lr ) {
  _dump_node( node, prefix, lr );
  if (node->m_left != 0)
    _dump_subtree( node->m_left,  prefix+"  ", 'L' );
  if (node->m_right != 0)
    _dump_subtree( node->m_right, prefix+"  ", 'R' );
}

template<class _Key, class _Value>
void RbTree<_Key,_Value>::_dump_tree() const {

  if( m_header->m_parent != 0) {
    _dump_node( m_header->m_parent, "Rt: " );
  }
  if( m_header->m_left != 0) {
    _dump_node( m_header->m_left, "Min:" );
  }
  if( m_header->m_right != 0) {
    _dump_node( m_header->m_right, "Max:" );
  }

  _dump_subtree( m_header->m_parent );
}

//------------------------------------------------------------------------
// Tree rotation and recoloring using the base node pointers
// Note these were inline in the original stl impl.
//------------------------------------------------------------------------
// Rotate Left
//------------------------------------------------------------------------
template<typename _Key, typename _Value>
void _RbTreeRotateLeft(
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
){
  xmem::MemPointer< _Node<_Key,_Value> > y = x->m_right;
  
  /* memoize values */
  typename RbTree<_Key,_Value>::NodePtr y_left = y->m_left;
  typename RbTree<_Key,_Value>::NodePtr x_parent = x->m_parent;
  
  x->m_right = y_left;
  
  if( y_left != 0 )
    y_left->m_parent = x;
  y->m_parent = x_parent;

  if (x == root)
    root = y;
  else if (x == x_parent->m_left)
    x_parent->m_left = y;
  else
    x_parent->m_right = y;
  y->m_left = x;
  x->m_parent = y;
}

//------------------------------------------------------------------------
// Rotate Right
//------------------------------------------------------------------------
template<typename _Key, typename _Value>
void _RbTreeRotateRight(
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
){
  xmem::MemPointer< _Node<_Key,_Value> > y = x->m_left;
  
  /* memoize values */
  typename RbTree<_Key,_Value>::NodePtr y_right = y->m_right;
  typename RbTree<_Key,_Value>::NodePtr x_parent = x->m_parent;
  
  x->m_left = y_right;

  if (y_right != 0)
    y_right->m_parent = x;
  y->m_parent = x_parent;

  if (x == root)
    root = y;
  else if (x == x_parent->m_right)
    x_parent->m_right = y;
  else
    x_parent->m_left = y;
  y->m_right = x;
  x->m_parent = y;
}

//------------------------------------------------------------------------
// Rebalance
//------------------------------------------------------------------------
template<typename _Key, typename _Value>
void _RbTreeRebalance(
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
){
  DB_ASSERT(( x != 0 ));
  DB_ASSERT(( root != 0 ));
  x->m_color = s_RbTreeRed;

  while (x != root && x->m_parent->m_color == s_RbTreeRed) {
    /* memoize values */
    typename RbTree<_Key,_Value>::NodePtr x_parent = x->m_parent;
    typename RbTree<_Key,_Value>::NodePtr x_parent_parent = x_parent->m_parent;
    
    if (x_parent == x_parent_parent->m_left) {
      xmem::MemPointer< _Node<_Key,_Value> > y = x_parent_parent->m_right;
      //XXX
      //if (y && y->m_color == s_RbTreeRed) {
      if (y != 0 && y->m_color == s_RbTreeRed) {
        x_parent->m_color = s_RbTreeBlack;
        y->m_color = s_RbTreeBlack;
        x_parent_parent->m_color = s_RbTreeRed;
        x = x_parent_parent;
      }
      else {
        if (x == x_parent->m_right) {
          x = x_parent;
          _RbTreeRotateLeft(x, root);
        }
        /* Re-memoize */
        x_parent = x->m_parent;
        x_parent_parent = x_parent->m_parent;

        x_parent->m_color = s_RbTreeBlack;
        x_parent_parent->m_color = s_RbTreeRed;
        _RbTreeRotateRight((xmem::MemPointer< _Node<_Key,_Value> >)x_parent_parent, root);
      }
    }
    else {
      xmem::MemPointer< _Node<_Key,_Value> > y = x_parent_parent->m_left;
      //XXX
      //if (y 0 && y->m_color == s_RbTreeRed) {
      if (y != 0 && y->m_color == s_RbTreeRed) {
        x_parent->m_color = s_RbTreeBlack;
        y->m_color = s_RbTreeBlack;
        x_parent_parent->m_color = s_RbTreeRed;
        x = x_parent_parent;
      }
      else {
        if (x == x_parent->m_left) {
          x = x_parent;
          _RbTreeRotateRight(x, root);
        }
        /* Re-memoize */
        x_parent = x->m_parent;
        x_parent_parent = x_parent->m_parent;

        x_parent->m_color = s_RbTreeBlack;
        x_parent_parent->m_color = s_RbTreeRed;
        _RbTreeRotateLeft((xmem::MemPointer< _Node<_Key,_Value> >)x_parent_parent, root);
      }
    }
  }
  root->m_color = s_RbTreeBlack;
} // end _RbTreeRebalance

//------------------------------------------------------------------------
// Rebalance for Erase
//------------------------------------------------------------------------
template<typename _Key, typename _Value>
xmem::MemPointer< _Node<_Key,_Value> >
_RbTreeRebalanceForErase(
    xmem::MemPointer< _Node<_Key,_Value> > _z,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& leftmost,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& rightmost
){
  xmem::MemPointer< _Node<_Key,_Value> > y = _z;
  xmem::MemPointer< _Node<_Key,_Value> > x = 0;
  xmem::MemPointer< _Node<_Key,_Value> > x_parent = 0;
  if (y->m_left == 0)     // _z has at most one non-null child. y == z.
    x = y->m_right;     // x might be null.
  else
    if (y->m_right == 0)  // _z has exactly one non-null child. y == z.
      x = y->m_left;    // x is not null.
    else {                   // _z has two non-null children.  Set y to
      y = y->m_right;   //   _z's successor.  x might be null.
      while (y->m_left != 0)
        y = y->m_left;
      x = y->m_right;
    }
  if (y != _z) {          // relink y in place of z.  y is z's successor
    _z->m_left->m_parent = y;
    y->m_left = _z->m_left;
    if (y != _z->m_right) {
      x_parent = y->m_parent;
      if (x) x->m_parent = y->m_parent;
      y->m_parent->m_left = x;      // y must be a child of m_left
      y->m_right = _z->m_right;
      _z->m_right->m_parent = y;
    }
    else
      x_parent = y;
    if (root == _z)
      root = y;
    else if (_z->m_parent->m_left == _z)
      _z->m_parent->m_left = y;
    else
      _z->m_parent->m_right = y;
    y->m_parent = _z->m_parent;
    std::swap(y->m_color, _z->m_color);
    y = _z;
    // y now points to node to be actually deleted
  }
  else {                        // y == _z
    x_parent = y->m_parent;
    if (x) x->m_parent = y->m_parent;
    if (root == _z)
      root = x;
    else
      if (_z->m_parent->m_left == _z)
        _z->m_parent->m_left = x;
      else
        _z->m_parent->m_right = x;
    if (leftmost == _z) {
      if (_z->m_right == 0)        // _z->m_left must be null also
        leftmost = _z->m_parent;
    // makes leftmost == m_header if _z == root
      else
        leftmost = xmem::MemValue< _Node<_Key,_Value> >::s_minimum(x);
    }
    if (rightmost == _z) {
      if (_z->m_left == 0)         // _z->m_right must be null also
        rightmost = _z->m_parent;
    // makes rightmost == m_header if _z == root
      else                      // x == _z->m_left
        rightmost = xmem::MemValue< _Node<_Key,_Value> >::s_maximum(x);
    }
  }
  if (y->m_color != s_RbTreeRed) {
    while (x != root && (x == 0 || x->m_color == s_RbTreeBlack))
      if (x == x_parent->m_left) {
        xmem::MemPointer< _Node<_Key,_Value> > w = x_parent->m_right;
        if (w->m_color == s_RbTreeRed) {
          w->m_color = s_RbTreeBlack;
          x_parent->m_color = s_RbTreeRed;
          _RbTreeRotateLeft(x_parent, root);
          w = x_parent->m_right;
        }
        if ((w->m_left == 0 ||
             w->m_left->m_color == s_RbTreeBlack) &&
            (w->m_right == 0 ||
             w->m_right->m_color == s_RbTreeBlack)) {
          w->m_color = s_RbTreeRed;
          x = x_parent;
          x_parent = x_parent->m_parent;
        } else {
          if (w->m_right == 0 ||
              w->m_right->m_color == s_RbTreeBlack) {
            if (w->m_left != 0) w->m_left->m_color = s_RbTreeBlack;
            w->m_color = s_RbTreeRed;
            _RbTreeRotateRight(w, root);
            w = x_parent->m_right;
          }
          w->m_color = x_parent->m_color;
          x_parent->m_color = s_RbTreeBlack;
          if (w->m_right != 0) w->m_right->m_color = s_RbTreeBlack;
          _RbTreeRotateLeft(x_parent, root);
          break;
        }
      } else {                  // same as above, with m_right <-> m_left.
        xmem::MemPointer< _Node<_Key,_Value> > w = x_parent->m_left;
        if (w->m_color == s_RbTreeRed) {
          w->m_color = s_RbTreeBlack;
          x_parent->m_color = s_RbTreeRed;
          _RbTreeRotateRight(x_parent, root);
          w = x_parent->m_left;
        }
        if ((w->m_right == 0 ||
             w->m_right->m_color == s_RbTreeBlack) &&
            (w->m_left == 0 ||
             w->m_left->m_color == s_RbTreeBlack)) {
          w->m_color = s_RbTreeRed;
          x = x_parent;
          x_parent = x_parent->m_parent;
        } else {
          if (w->m_left == 0 ||
              w->m_left->m_color == s_RbTreeBlack) {
            if (w->m_right != 0) w->m_right->m_color = s_RbTreeBlack;
            w->m_color = s_RbTreeRed;
            _RbTreeRotateLeft(w, root);
            w = x_parent->m_left;
          }
          w->m_color = x_parent->m_color;
          x_parent->m_color = s_RbTreeBlack;
          if (w->m_left != 0) w->m_left->m_color = s_RbTreeBlack;
          _RbTreeRotateRight(x_parent, root);
          break;
        }
      }
    if (x) x->m_color = s_RbTreeBlack;
  }
  return y;
} // end RbTreeRebalanceForErase
