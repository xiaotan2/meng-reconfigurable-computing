//========================================================================
// PolyHS rbtree iterators
//========================================================================
// Author  : Ritchie Zhao
// Date    : July 17, 2015
// Project : Polymorphic Hardware Specialization
//

#ifndef POLYDSU_RBTREE_RBTREE_ITERATOR_H
#define POLYDSU_RBTREE_RBTREE_ITERATOR_H

#include <cstddef>
#include <iterator>
#include <assert.h>

#include "polydsu_rbtree/RbTreeProxy.h"

//------------------------------------------------------------------------
// template RbTreeIterator
//------------------------------------------------------------------------
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
struct RbTreeIterator {
  typedef std::bidirectional_iterator_tag iterator_category;
  typedef ptrdiff_t                       difference_type;

  typedef _VProxy             reference;
  typedef _KProxy             key_reference;
  typedef _VProxy             val_reference;
  typedef NodePtr             pointer;
  typedef RbTreeIterator<_Key, _Value, _KProxy, _VProxy, NodePtr>
                              iterator;

  NodePtr m_node;

  // default constructor
  RbTreeIterator( xmem::Opaque opq,
                  xmem::MemReqStream& memreq, xmem::MemRespStream& memresp)
    : m_node( 0, opq, memreq, memresp )
  {}
  // constructor from pointer
  RbTreeIterator( NodePtr x )
    : m_node( x )
  {}
  // copy constructor
  RbTreeIterator( const iterator& it )
    : m_node( it.m_node )
  {}

  void _increment();
  void _decrement();

  val_reference operator*() const { return m_node->m_value; }
  pointer  operator->() const { return m_node; }
  val_reference value() const { return m_node->m_value; }
  key_reference key() const { return m_node->m_key; }

  iterator& operator++() { _increment(); return *this; }
  iterator  operator++(int) {
    iterator temp = *this;
    _increment();
    return temp;
  }
  iterator& operator--() { _decrement(); return *this; }
  iterator  operator--(int) {
    iterator temp = *this;
    _decrement();
    return temp;
  }
};

//------------------------------------------------------------------------
// template RbTreeFindIterator
//------------------------------------------------------------------------
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
struct RbTreeFindIterator {
  typedef std::bidirectional_iterator_tag iterator_category;
  typedef ptrdiff_t                       difference_type;

  typedef _VProxy             reference;
  typedef _KProxy             key_reference;
  typedef _VProxy             val_reference;
  typedef NodePtr             pointer;
  typedef RbTreeFindIterator<_Key, _Value, _KProxy, _VProxy, NodePtr>
                              iterator;

  const NodePtr&  m_header;   // tree header
  NodePtr         m_node;     // current node
  NodePtr         m_parent;   // Last node which is not less than _k.
  _Key            m_key;

  // constructor from pointers
  RbTreeFindIterator( const NodePtr& header, NodePtr x, NodePtr y, const _Key& k )
    : m_header( header ),
      m_node( x ),
      m_parent( y ),
      m_key( k )
  {}
  // copy constructor
  RbTreeFindIterator( const iterator& it )
    : m_header( it.m_header ),
      m_node( it.m_node ),
      m_parent( it.m_parent ),
      m_key( it.m_key )
  {}

  void _increment();
  void _decrement();

  bool found() const;
  val_reference operator*() const { return m_parent->m_value; }
  pointer  operator->() const { return m_parent; }
  val_reference value() const { return m_parent->m_value; }
  key_reference key() const { return m_parent->m_key; }

  iterator& operator++() { _increment(); return *this; }
  iterator  operator++(int) {
    iterator temp = *this;
    _increment();
    return temp;
  }
  iterator& operator--() { _decrement(); return *this; }
  iterator  operator--(int) {
    iterator temp = *this;
    _decrement();
    return temp;
  }
};

//------------------------------------------------------------------------
// RbTreeIterator equality operators
//------------------------------------------------------------------------
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
inline bool operator==(
    const RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> x,
    const RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> y
){
  return x.m_node == y.m_node;
}
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
inline bool operator!=(
    const RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> x,
    const RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> y
){
  return x.m_node != y.m_node;
}

//------------------------------------------------------------------------
// RbTreeFindIterator equality operators
//------------------------------------------------------------------------
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
inline bool operator==(
    const RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> x,
    const RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> y
){
  return x.m_node == y.m_node;
}
template<class _Key, class _Value, class _KProxy, class _VProxy, class NodePtr>
inline bool operator!=(
    const RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> x,
    const RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr> y
){
  return x.m_node != y.m_node;
}

//------------------------------------------------------------------------
// RbTreeIterator increment
//------------------------------------------------------------------------
template<class _Key, class _Value,
         class _KProxy, class _VProxy, class NodePtr>
void RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr>::_increment() {
  NodePtr m_node_right = m_node->m_right;
  if( m_node_right != 0 ) {
    m_node = m_node_right;
    /*while( m_node->m_left != 0 ) {
      m_node = m_node->m_left;
    }*/
    while(1) {
      xmem::MemPointer< _Node<_Key,_Value> > m_node_left = m_node->m_left;
      if ( m_node_left == 0 ) break;
      m_node = m_node_left;
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
}

//------------------------------------------------------------------------
// RbTreeIterator decrement
//------------------------------------------------------------------------
template<class _Key, class _Value,
         class _KProxy, class _VProxy, class NodePtr>
void RbTreeIterator<_Key,_Value,_KProxy,_VProxy,NodePtr>::_decrement() {
  if( m_node->m_color == s_RbTreeRed && m_node->m_parent->m_parent == m_node) {
    m_node = m_node->m_right;
  }
  else if( m_node->m_left != 0 ) {
    NodePtr y = m_node->m_left;
    /*while( y->m_right != 0 )
      y = y->m_right;*/
    while(1) {
      xmem::MemPointer< _Node<_Key,_Value> > y_right = y->m_right;
      if ( y_right == 0 ) break;
      y = y_right;
    }
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
}

//------------------------------------------------------------------------
// RbTreeFindIterator increment
//------------------------------------------------------------------------
template<class _Key, class _Value,
         class _KProxy, class _VProxy, class NodePtr>
void RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr>::_increment() {
  if (m_node != 0) {
    if (!((_Key)m_node->m_key < m_key))
      m_parent = m_node, m_node = m_node->m_left;
    else
      m_node = m_node->m_right;
  }
}

//------------------------------------------------------------------------
// RbTreeFindIterator found
//------------------------------------------------------------------------
template<class _Key, class _Value,
         class _KProxy, class _VProxy, class NodePtr>
bool RbTreeFindIterator<_Key,_Value,_KProxy,_VProxy,NodePtr>::found() const
{
  return ( (m_parent == m_header) || (m_key < (_Key)m_parent->m_key) )
    ? false : true;
}
  
#endif
