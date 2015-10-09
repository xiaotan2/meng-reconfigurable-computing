//========================================================================
// RbTree proxies header
//========================================================================
// This file contains proxy objects for use in RbTree

#ifndef POLYDSU_BINTREE_BIN_TREE_PROXY_H
#define POLYDSU_BINTREE_BIN_TREE_PROXY_H

#include "xmem/MemProxy.h"

//------------------------------------------------------------------------
// Forward Declarations
//------------------------------------------------------------------------
//template<typename K, typename V> class _Node;
//template<typename K, typename V> struct MemValue< _Node<K,V> >;

//------------------------------------------------------------------------
// This should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename Value>
struct _Node {
  _Node*            m_parent;
  _Node*            m_left;
  _Node*            m_right;
  Value             value;
};

namespace xmem {

  //----------------------------------------------------------------------
  // Tree NodeProxy
  //----------------------------------------------------------------------
  template<typename _Value>
  struct MemValue< _Node<_Value> > {
    typedef MemValue<_Value>              ValueType;
    typedef MemPointer< _Node<_Value> >   NodePointer;
    typedef MemValue< NodePointer >       NodePtrProxy;

    NodePtrProxy   m_parent;
    NodePtrProxy   m_left;
    NodePtrProxy   m_right;
    ValueType      m_value;

    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_parent( base_ptr, opq, memreq, memresp ),
        m_left  ( base_ptr+PTR_SIZE, opq, memreq, memresp ),
        m_right ( base_ptr+2*PTR_SIZE, opq, memreq, memresp ),
        m_value ( base_ptr+3*PTR_SIZE, opq, memreq, memresp )
    {}

    //------------------------------------------------------------
    // Get/Set Address
    //------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_parent.set_addr( addr );
      m_left.set_addr  ( addr+PTR_SIZE );
      m_right.set_addr ( addr+2*PTR_SIZE );
      m_value.set_addr ( addr+3*PTR_SIZE );
    }

    xmem::Address get_addr() const { return m_parent.get_addr(); }
    
    //--------------------------------------------------------------------
    // Get/Set Opaque
    //--------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      m_parent.set_opq ( opq );
      m_left.set_opq   ( opq );
      m_right.set_opq  ( opq );
      m_value.set_opq  ( opq );
    }

    xmem::Opaque get_opq() const { return m_parent.get_opq(); }
    
    //--------------------------------------------------------------------
    
    //--------------------------------------------------------------------
    // Get mem iface
    //--------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return m_parent.memreq(); }
    xmem::MemRespStream& memresp() const { return m_parent.memresp(); }

    static size_t size() {
      return 3*PTR_SIZE + ValueType::size();
    }
  };

};

#endif /* POLYDSU_BINTREE_RB_TREE_PROXY_H */
