//========================================================================
// RbTree proxies header
//========================================================================
// This file contains proxy objects for use in RbTree

#ifndef POLYDSU_RBTREE_RB_TREE_PROXY_H
#define POLYDSU_RBTREE_RB_TREE_PROXY_H

#include "xmem/MemProxy.h"

typedef bool RbTreeColorType;
const RbTreeColorType s_RbTreeRed = false;
const RbTreeColorType s_RbTreeBlack = true;

//------------------------------------------------------------------------
// Forward Declarations
//------------------------------------------------------------------------
//template<typename K, typename V> class _Node;
//template<typename K, typename V> struct MemValue< _Node<K,V> >;

//------------------------------------------------------------------------
// This should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename K, typename V>
struct _Node {
  _Node*            m_parent;
  _Node*            m_left;
  _Node*            m_right;
  RbTreeColorType   m_color;
  K                 key;
  V                 value;
};

namespace xmem {

  //----------------------------------------------------------------------
  // Tree NodeProxy
  //----------------------------------------------------------------------
  template<typename K, typename V>
  struct MemValue< _Node<K,V> > {
    typedef MemValue<K>                   ValueType;
    typedef MemValue<V>                   KeyType;
    typedef MemValue<RbTreeColorType>     ColorType;
    typedef MemPointer< _Node<K,V> >      NodePointer;
    typedef MemValue< NodePointer >       NodePtrProxy;

    NodePtrProxy   m_parent;
    NodePtrProxy   m_left;
    NodePtrProxy   m_right;
    ColorType      m_color;
    KeyType        m_key;
    ValueType      m_value;

    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_parent( base_ptr, opq, memreq, memresp ),
        m_left  ( base_ptr+PTR_SIZE, opq, memreq, memresp ),
        m_right ( base_ptr+2*PTR_SIZE, opq, memreq, memresp ),
        m_color ( base_ptr+3*PTR_SIZE, opq, memreq, memresp ),
        m_key   ( base_ptr+3*PTR_SIZE+ColorType::size(), opq, memreq, memresp ),
        m_value ( base_ptr+3*PTR_SIZE+ColorType::size()+KeyType::size(),
                  opq, memreq, memresp )
    {}

    //--------------------------------------------------------------------
    // Methods
    //--------------------------------------------------------------------
    static NodePointer s_minimum( NodePointer x ) {
      while( x->m_left != 0 ) x = x->m_left;
      return x;
    }
    static NodePointer s_maximum( NodePointer x ) {
      while( x->m_right != 0 ) x = x->m_right;
      return x;
    }

    //--------------------------------------------------------------------
    // Get/Set Address
    //--------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_parent.set_addr( addr );
      m_left.set_addr  ( addr+PTR_SIZE );
      m_right.set_addr ( addr+2*PTR_SIZE );
      m_color.set_addr ( addr+3*PTR_SIZE );
      m_key.set_addr   ( addr+3*PTR_SIZE + ColorType::size() );
      m_value.set_addr ( addr+3*PTR_SIZE + ColorType::size() + KeyType::size() );
    }

    xmem::Address get_addr() const { return m_parent.get_addr(); }
  
    //--------------------------------------------------------------------
    // Get/Set Opaque
    //--------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      m_parent.set_opq ( opq );
      m_left.set_opq   ( opq );
      m_right.set_opq  ( opq );
      m_color.set_opq  ( opq );
      m_key.set_opq    ( opq );
      m_value.set_opq  ( opq );
    }

    xmem::Opaque get_opq() const { return m_parent.get_opq(); }
    
    //--------------------------------------------------------------------
    // Get mem iface
    //--------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return m_parent.memreq(); }
    xmem::MemRespStream& memresp() const { return m_parent.memresp(); }

    static size_t size() {
      return 3*PTR_SIZE+ColorType::size()+KeyType::size()+ValueType::size();
    }
  };

};

#endif /* POLYDSU_RBTREE_RB_TREE_PROXY_H */

