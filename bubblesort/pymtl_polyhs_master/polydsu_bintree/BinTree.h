//========================================================================
// PolyHS bintree
//========================================================================
// Author  : Ritchie Zhao
// Date    : July 17, 2015
// Project : Polymorphic Hardware Specialization
//

#ifndef POLYDSU_BINTREE_BINTREE_H
#define POLYDSU_BINTREE_BINTREE_H

#include <cstddef>
#include <assert.h>

#include "polydsu_bintree/BinTreeProxy.h"
#include "polydsu_bintree/BinTreeIterator.h"

//------------------------------------------------------------------------
// tree rotation and recoloring
//------------------------------------------------------------------------
template<typename _Value>
void  _BinTreeRotateLeft ( 
    xmem::MemPointer< _Node<_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Value> > >& root
);
template<typename _Value>
void  _BinTreeRotateRight(
    xmem::MemPointer< _Node<_Value> > x,
    xmem::MemValue< xmem::MemPointer< _Node<_Value> > >& root
);

//------------------------------------------------------------------------
// BinTree template
//------------------------------------------------------------------------
template<class _Value>
class BinTree {
  public:
    typedef xmem::MemValue< _Node<_Value> >     Node;
    typedef typename Node::NodePointer          NodePtr;
    typedef typename Node::NodePtrProxy         NodePtrProxy;
  protected:
    typedef xmem::MemValue<_Value>              ValueProxy;
    typedef size_t                              size_type;
    typedef ptrdiff_t                           difference_type;

  public:
    NodePtr m_header;
    size_type m_node_count;

  //----------------------------------------------------------------------
  // Iterator Types
  //----------------------------------------------------------------------
  public:

    typedef _IteratorBase< _Value, ValueProxy, NodePtr >
      base_iterator;
    typedef _PreorderIterator< _Value, ValueProxy, NodePtr >
      preorder_iterator;
    typedef _PreorderIterator< _Value, const ValueProxy, NodePtr >
      const_preorder_iterator;
    typedef _InorderIterator< _Value, ValueProxy, NodePtr >
      inorder_iterator;
    typedef _InorderIterator< _Value, const ValueProxy, NodePtr >
      const_inorder_iterator;

    typedef inorder_iterator        iterator;
    typedef const_inorder_iterator  const_iterator;

  //----------------------------------------------------------------------
  // Allocation/Deallocation
  //----------------------------------------------------------------------
  protected:

    NodePtr m_create_header(xmem::Opaque opq,
            xmem::MemReqStream& memreq, xmem::MemRespStream& memresp );
    NodePtr m_create_node(const _Value& x);
    void m_destroy_node( NodePtr p );
    NodePtr m_clone_node ( NodePtr x );

  //----------------------------------------------------------------------
  // Basic Operations
  //----------------------------------------------------------------------
  public:

    static NodePtrProxy&    s_left( NodePtr x )
      { return (x->m_left); }
    static NodePtrProxy&    s_right( NodePtr x )
      { return (x->m_right); }
    static NodePtrProxy&    s_parent( NodePtr x )
      { return (x->m_parent); }
    static ValueProxy&      s_value( NodePtr x )
      { return (x->m_value); }

  //----------------------------------------------------------------------
  // Constructors / Destructors
  //----------------------------------------------------------------------
  public:

    BinTree( xmem::Opaque opq,
             xmem::MemReqStream& memreq, xmem::MemRespStream& memresp );
    BinTree( xmem::Address header_addr, xmem::Opaque opq,
             xmem::MemReqStream& memreq, xmem::MemRespStream& memresp );
    BinTree( const BinTree& x );
    ~BinTree();

  //----------------------------------------------------------------------
  // Operators
  //----------------------------------------------------------------------

    BinTree& operator=(const BinTree& x);

  //----------------------------------------------------------------------
  // Private Helper Methods
  //----------------------------------------------------------------------
  private:

    void m_insert_left (NodePtr x, NodePtr new_node);
    void m_insert_right(NodePtr x, NodePtr new_node);
    NodePtr m_copy(NodePtr x);
    void m_erase(NodePtr x);
    void empty_initialize();

    NodePtr NullPtr() const { return NodePtr(0, m_header.get_opq(),
                                     m_header.memreq(), m_header.memresp()); }

  //----------------------------------------------------------------------
  // User Methods
  //----------------------------------------------------------------------
  public:

    iterator begin() { return begin_inorder(); }
    iterator end() { return end_inorder(); }

    preorder_iterator begin_preorder();
    preorder_iterator end_preorder();
    inorder_iterator  begin_inorder();
    inorder_iterator  end_inorder();

    NodePtr root() { return m_header->m_left; }
    
    bool empty() const { return m_node_count == 0; }
    size_type size() const { return m_node_count; }
    size_type max_size() const { return size_type(-1); }

    void swap(BinTree& t) {
      std::swap(m_header, t.m_header);
      std::swap(m_node_count, t.m_node_count);
    }

  public:

    iterator set_root( const _Value& v );
    iterator set_root( NodePtr node );
    
    template<class iter> iter insert_left (iter pos, const _Value& v);
    template<class iter> iter insert_right(iter pos, const _Value& v);
    template<class iter> iter insert_left (iter pos, NodePtr node);
    template<class iter> iter insert_right(iter pos, NodePtr node);

    template<class iter> void erase(iter pos);
    void clear();

  public:
                                  // set operations:
    // finds iterator to x
    template<class iter> iter find(const _Value& x) const;
    // counts number of elems with key equal to x (0 or 1)
    size_type count(const _Value& x) const;

  public:
                                  // Debugging.
    static void _dump_node( const NodePtr node,
                            const std::string prefix="", const char lr='x' );
    static void _dump_subtree( const NodePtr node,
                            const std::string prefix="", const char lr='x' );
    void _dump_tree() const;

};

#include "polydsu_bintree/BinTree.inl"
#endif /* POLYDSU_BINTREE_BINTREE_H */

