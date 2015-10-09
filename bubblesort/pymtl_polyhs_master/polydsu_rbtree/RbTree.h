//========================================================================
// PolyHS rbtree
//========================================================================
// Author  : Ritchie Zhao
// Date    : July 17, 2015
// Project : Polymorphic Hardware Specialization
//

#ifndef POLYDSU_RBTREE_RBTREE_H
#define POLYDSU_RBTREE_RBTREE_H

#include <assert.h>

#include "polydsu_rbtree/RbTreeProxy.h"
#include "polydsu_rbtree/RbTreeIterator.h"

//------------------------------------------------------------------------
// tree rotation and recoloring
//------------------------------------------------------------------------

template<typename _Key, typename _Value>
void  _RbTreeRotateLeft (
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
  );
template<typename _Key, typename _Value>
void  _RbTreeRotateRight(
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
  );
template<typename _Key, typename _Value>
void  _RbTreeRebalance  (
    xmem::MemPointer< _Node<_Key,_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root
  );
template<typename _Key, typename _Value>
xmem::MemPointer< _Node<_Key,_Value> >
_RbTreeRebalanceForErase( 
    xmem::MemPointer< _Node<_Key,_Value> > _z,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& root,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& leftmost,
    xmem::MemValue< xmem::MemPointer< _Node<_Key,_Value> > >& rightmost
 );

//------------------------------------------------------------------------
// RbTree template
//------------------------------------------------------------------------
//   The STL rbtree is further templated on the KeyComp and Allocator.
//   KeyComp is replaced by just key::operator==, and the Allocator
//   is just new and delete for now.
//
//   Both _Key and _Value are stored at a node, and an insert operation
//   must be done with both _Key and _Value.
template<class _Key, class _Value>
class RbTree {
public:
  typedef xmem::MemValue< _Node<_Key,_Value> > Node;
  typedef typename Node::NodePointer          NodePtr;
  typedef typename Node::NodePtrProxy         NodePtrProxy;
  typedef RbTreeColorType                     ColorType;
protected:
  typedef xmem::MemValue<_Key>                 KeyProxy;
  typedef xmem::MemValue<_Value>               ValueProxy;
  typedef xmem::MemValue<ColorType>            ColorProxy;
  typedef size_t                              size_type;
  typedef ptrdiff_t                           difference_type;

public:
  // The header is used to quickly access the root node, leftmost node,
  // and rightmost node
  NodePtr m_header;
  size_type m_node_count;

//------------------------------------------------------------------------
// Iterator Types
//------------------------------------------------------------------------
public:

  typedef RbTreeIterator< _Key, _Value, KeyProxy, ValueProxy,
          NodePtr > iterator;
  typedef RbTreeIterator< _Key, _Value, const KeyProxy, const ValueProxy,
          NodePtr > const_iterator;
  typedef RbTreeFindIterator< _Key, _Value, const KeyProxy, const ValueProxy,
          NodePtr > find_iterator;

//------------------------------------------------------------------------
// Allocation/Deallocation
//------------------------------------------------------------------------
protected:

  NodePtr m_create_node(xmem::Address mem, const _Key& k, const _Value& x);
  void m_destroy_node( NodePtr p );
  NodePtr m_clone_node ( NodePtr x );

//------------------------------------------------------------------------
// Basic Operations
//------------------------------------------------------------------------
public:

  NodePtrProxy m_root() const
    { return m_header->m_parent; }
  /*NodePtrProxy m_leftmost() const
    { return m_header->m_left; }
  NodePtrProxy m_rightmost() const
    { return m_header->m_right; }*/

  static NodePtrProxy&    s_left( NodePtr x )
    { return (x->m_left); }
  static NodePtrProxy&    s_right( NodePtr x )
    { return (x->m_right); }
  static NodePtrProxy&    s_parent( NodePtr x )
    { return (x->m_parent); }
  static ValueProxy&      s_value( NodePtr x )
    { return (x->m_value); }
  static const KeyProxy&  s_key( NodePtr x )
    { return (x->m_key); }
  static ColorProxy&      s_color( NodePtr x )
    { return (x->m_color); }

  static NodePtr s_minimum( NodePtr x ) {
    return Node::s_minimum( x );
  }
  static NodePtr s_maximum( NodePtr x ) {
    return Node::s_maximum( x );
  }

//------------------------------------------------------------------------
// Constructors / Destructors
//------------------------------------------------------------------------
public:

  RbTree( NodePtr header );
  RbTree( xmem::Address mem, xmem::Opaque opq, 
          xmem::MemReqStream& memreq,
          xmem::MemRespStream& memresp );
  ~RbTree();

//------------------------------------------------------------------------
// Private Helper Methods
//------------------------------------------------------------------------
private:

  iterator m_insert( xmem::Address mem,
                     NodePtr x, NodePtr y,
                     const _Key& k, const _Value& v );
  NodePtr m_copy(NodePtr x, NodePtr p);
  void m_erase(NodePtr x);

//------------------------------------------------------------------------
// User Methods
//------------------------------------------------------------------------
public:
                                // accessors:
  iterator begin() { return (NodePtr)m_header->m_left; }
  const_iterator begin() const { return (NodePtr)m_header->m_left; }
  iterator end() { return m_header; }
  const_iterator end() const { return m_header; }
  /*reverse_iterator rbegin() { return reverse_iterator(end()); }
  const_reverse_iterator rbegin() const {
    return const_reverse_iterator(end());
  }
  reverse_iterator rend() { return reverse_iterator(begin()); }
  const_reverse_iterator rend() const {
    return const_reverse_iterator(begin());
  }*/

  // find iterator
  find_iterator begin_find( const _Key& k ) const {
    return find_iterator(
        m_header, (NodePtr)m_root(), (NodePtr)m_header, k
    );
  }
  find_iterator end_find( const _Key& k ) const {
    return find_iterator(
        m_header,
        NodePtr( 0, m_header.get_opq(), m_header.memreq(), m_header.memresp() ),
        (NodePtr)m_header,
        k
    );
  }

  bool empty() const { return m_node_count == 0; }
  size_type size() const { return m_node_count; }
  size_type max_size() const { return size_type(-1); }

  void swap(RbTree& t) {
    std::swap(m_header, t.m_header);
    std::swap(m_node_count, t.m_node_count);
  }

public:
                                // insert/erase
  // RZ:  insert_equal not supported as it is not used by
  //      map or set
  std::pair<iterator,bool> insert_unique(
      xmem::Address mem,
      const _Key& k, const _Value& x
  );
  iterator insert_unique(
      iterator position,
      xmem::Address,
      const _Key& k, const _Value& x
  );
  //void insert_unique(const_iterator first, const_iterator last);
  //void insert_unique(iterator first, iterator last);
  //void insert_unique(const _Value* first, const _Value* last);

  void erase(iterator position);
  size_type erase(const _Key& x);
  void erase(iterator first, iterator last);
  void erase(const _Key* first, const _Key* last);
  void empty_initialize();
  void clear();

public:
                                // set operations:
  // finds iterator to x
  iterator find(const _Key& x);
  const_iterator find(const _Key& x) const;
  // counts number of elems with key equal to x (0 or 1)
  size_type count(const _Key& x) const;
  // returns an iterator to the first elem with key >= x
  iterator lower_bound(const _Key& x);
  const_iterator lower_bound(const _Key& x) const;
  // returns an iterator to the first elem with key > x
  iterator upper_bound(const _Key& x);
  const_iterator upper_bound(const _Key& x) const;

  // returns bounds of a range containing elems with key == x
  std::pair<iterator,iterator> equal_range(const _Key& x) {
    return std::pair<iterator, iterator>(
        lower_bound(x), upper_bound(x));
  }
  std::pair<const_iterator, const_iterator> equal_range(const _Key& x) const {
    return std::pair<const_iterator,const_iterator>(
        lower_bound(x), upper_bound(x));
  }

public:
                                // Debugging.
  int black_count( NodePtr node, NodePtr root ) const;
  bool _rb_verify() const;
  static void _dump_node( const NodePtr node, const std::string prefix="", const char lr='x' );
  static void _dump_subtree( const NodePtr node, const std::string prefix="", const char lr='x' );
  void _dump_tree() const;

};

#include "polydsu_rbtree/RbTree.inl"
#endif /* POLYDSU_RBTREE_RBTREE_H */

