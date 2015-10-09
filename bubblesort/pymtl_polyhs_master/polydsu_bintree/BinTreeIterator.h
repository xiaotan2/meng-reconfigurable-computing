//========================================================================
// PolyHS bintree iterators
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : July 19, 2015
// Project : Polymorphic Hardware Specialization

#ifndef POLYDSU_BINTREE_BINTREE_ITERATOR_H
#define POLYDSU_BINTREE_BINTREE_ITERATOR_H

#include <iterator>

#include "polydsu_bintree/BinTreeProxy.h"

//------------------------------------------------------------------------
// template _IteratorBase
//------------------------------------------------------------------------
// Accessors only, no traversal logic
template<class _Value, class _VProxy, class NodePtr>
struct _IteratorBase {
  typedef std::bidirectional_iterator_tag iterator_category;
  typedef ptrdiff_t                       difference_type;
  typedef _VProxy                         reference;
  typedef NodePtr                         pointer;

  NodePtr m_node;

  // default constructor
  _IteratorBase( xmem::MemReqStream& memreq, xmem::MemRespStream& memresp)
    : m_node( 0, memreq, memresp )
  {}
  // constructor from pointer
  _IteratorBase( NodePtr x )
    : m_node( x )
  {}
  // copy constructor
  _IteratorBase( const _IteratorBase& it )
    : m_node( it.m_node )
  {}
  
  reference operator* () const { return m_node->m_value; }
  pointer   operator->() const { return m_node; }
};

//------------------------------------------------------------------------
// Depth-first pre-order iterator
// self -> left -> right
//------------------------------------------------------------------------
template<class _Value, class _VProxy, class NodePtr>
struct _PreorderIterator : public _IteratorBase<_Value,_VProxy,NodePtr> {

  typedef _PreorderIterator<_Value, _VProxy, NodePtr>   Iterator;
  typedef _IteratorBase<_Value, _VProxy, NodePtr>       IteratorBase;

  _PreorderIterator() : IteratorBase( 0 ) {}
  _PreorderIterator( NodePtr x ) : IteratorBase( x ) {}
  _PreorderIterator( const IteratorBase& base ) : IteratorBase( base.m_node )
  {}

  bool operator==(const Iterator& rhs) const {
    return this->m_node == rhs.m_node;
  }
  bool operator!=(const Iterator& rhs) const {
    return this->m_node != rhs.m_node;
  }
  
  Iterator& operator++() {
    if( this->m_node->m_left != 0 ) {
      this->m_node = this->m_node->m_left;
    }
    else if ( this->m_node->m_right != 0 ) {
      this->m_node = this->m_node->m_right;
    }
    else {
      // search for a parent where we are the left child
      NodePtr y = this->m_node->m_parent;
      while( y != 0 && this->m_node == y->m_right ) {
        this->m_node = y;
        y = y->m_parent;
      }
      if( y != 0 ) {
      }

    }

  }

  Iterator& operator--() {
    if( this->m_node->m_left != 0 ) {
    }

    return *this;
  }

  Iterator& operator++(int) {
    Iterator temp = *this;
    ++(*this);
    return temp;
  }

  Iterator& operator--(int) {
    Iterator temp = *this;
    --(*this);
    return temp;
  }
};

//------------------------------------------------------------------------
// Depth-first in-order iterator
// left -> self -> right
//------------------------------------------------------------------------
template<class _Value, class _VProxy, class NodePtr>
struct _InorderIterator : public _IteratorBase<_Value,_VProxy,NodePtr> {

  typedef _InorderIterator<_Value, _VProxy, NodePtr>  Iterator;
  typedef _IteratorBase<_Value, _VProxy, NodePtr>     IteratorBase;

  _InorderIterator() : IteratorBase( 0 ) {}
  _InorderIterator( NodePtr x ) : IteratorBase( x ) {}
  _InorderIterator( const IteratorBase& base ) : IteratorBase( base.m_node )
  {}

  bool operator==(const Iterator& rhs) const {
    return this->m_node == rhs.m_node;
  }
  bool operator!=(const Iterator& rhs) const {
    return this->m_node != rhs.m_node;
  }

  Iterator& operator++() {
    NodePtr m_node_right = this->m_node->m_right;

    if( m_node_right != 0 ) {
      this->m_node = m_node_right;
      /*while( this->m_node->m_left != 0 ) {
        this->m_node = this->m_node->m_left;
      }*/
      while( 1 ) {
        NodePtr m_node_left = this->m_node->m_left;
        if ( m_node_left == 0 ) break;
        this->m_node = m_node_left;
      }
    }
    else {
      NodePtr y = this->m_node->m_parent;
      while( y != 0 && this->m_node == y->m_right ) {
        this->m_node = y;
        y = y->m_parent;
      }
      if ( y != 0 )
        this->m_node = y;
    }
    return *this;
  }

  Iterator& operator--() {
    NodePtr m_node_left = this->m_node->m_left;

    if( m_node_left != 0 ) {
      NodePtr y = m_node_left;
      /*while( y->m_right != 0 )
        y = y->m_right;*/
      while( 1 ) {
        NodePtr y_right = y->m_right;
        if ( y_right == 0 ) break;
        y = y_right;
      }
      this->m_node = y;
    }
    else {
      NodePtr y = this->m_node->m_parent;
      while( this->m_node == y->m_left ) {
        this->m_node = y;
        y = y->m_parent;
      }
      this->m_node = y;
    }
    return *this;
  }

  Iterator& operator++(int) {
    Iterator temp = *this;
    ++(*this);
    return temp;
  }

  Iterator& operator--(int) {
    Iterator temp = *this;
    --(*this);
    return temp;
  }
};

//------------------------------------------------------------------------
// Depth-first post-order iterator
// left -> right -> self
//------------------------------------------------------------------------
template<class _Value, class _VProxy, class NodePtr>
struct _PostorderIterator : public _IteratorBase<_Value,_VProxy,NodePtr> {

  typedef _PostorderIterator<_Value, _VProxy, NodePtr>  Iterator;
  typedef _IteratorBase<_Value, _VProxy, NodePtr>       IteratorBase;

  _PostorderIterator() : IteratorBase( 0 ) {}
  _PostorderIterator( NodePtr x ) : IteratorBase( x ) {}
  _PostorderIterator( const IteratorBase& base ) : IteratorBase( base.m_node )
  {}

  bool operator==(const Iterator& rhs) const {
    return this->m_node == rhs.m_node;
  }
  bool operator!=(const Iterator& rhs) const {
    return this->m_node != rhs.m_node;
  }
  
  Iterator& operator++() {
    return *this;
  }

  Iterator& operator--() {
    return *this;
  }

  Iterator& operator++(int) {
    Iterator temp = *this;
    ++(*this);
    return temp;
  }

  Iterator& operator--(int) {
    Iterator temp = *this;
    --(*this);
    return temp;
  }
};

//------------------------------------------------------------------------
// Leaf iterator
//------------------------------------------------------------------------
template<class _Value, class _VProxy, class NodePtr>
struct _LeafIterator : public _IteratorBase<_Value,_VProxy,NodePtr> {

  typedef _LeafIterator<_Value, _VProxy, NodePtr>  Iterator;
  typedef _IteratorBase<_Value, _VProxy, NodePtr>  IteratorBase;

  _LeafIterator() : IteratorBase( 0 ) {}
  _LeafIterator( NodePtr x ) : IteratorBase( x ) {}
  _LeafIterator( const IteratorBase& base ) : IteratorBase( base.m_node )
  {}

  bool operator==(const Iterator& rhs) const {
    return this->m_node == rhs.m_node;
  }
  bool operator!=(const Iterator& rhs) const {
    return this->m_node != rhs.m_node;
  }
  
  Iterator& operator++() {
    return *this;
  }

  Iterator& operator--() {
    return *this;
  }

  Iterator& operator++(int) {
    Iterator temp = *this;
    ++(*this);
    return temp;
  }

  Iterator& operator--(int) {
    Iterator temp = *this;
    --(*this);
    return temp;
  }
};

#endif
