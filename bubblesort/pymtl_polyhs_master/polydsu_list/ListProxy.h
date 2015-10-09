//========================================================================
// list proxies header
//========================================================================
// This file contains proxy objects for use with List

#ifndef POLYDSU_LIST_LIST_PROXY_H
#define POLYDSU_LIST_LIST_PROXY_H

#include <stdlib.h>
#include <stdio.h>

#include "xmem/MemProxy.h"

//------------------------------------------------------------------------
// This should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename T>
class _ListNode {
  _ListNode* m_prev;
  _ListNode* m_next;
  T m_value;
};

namespace xmem {
  //----------------------------------------------------------------------
  // List MemValue
  //----------------------------------------------------------------------
  template<typename T>
  class MemValue< _ListNode<T> > {
    public:
      MemValue< MemPointer< _ListNode<T> > > m_prev;
      MemValue< MemPointer< _ListNode<T> > > m_next;
      MemValue<T> m_value;

  //----------------------------------------------------------------------
  // Constructors
  //----------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_prev ( base_ptr, opq, memreq, memresp ),
        m_next ( base_ptr+PTR_SIZE, opq, memreq, memresp ),
        m_value( base_ptr+PTR_SIZE+PTR_SIZE, opq, memreq, memresp )
    {}

  //----------------------------------------------------------------------
  // Get/Set Address
  //----------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_prev.set_addr ( addr );
      m_next.set_addr ( addr+PTR_SIZE );
      m_value.set_addr( addr+PTR_SIZE+PTR_SIZE );
    }

    xmem::Address get_addr() const { return m_prev.get_addr(); }
  
  //----------------------------------------------------------------------
  // Get/Set Opaque
  //----------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      m_prev.set_opq ( opq );
      m_next.set_opq ( opq );
      m_value.set_opq( opq );
    }

    xmem::Opaque get_opq() const { return m_prev.get_opq(); }

  //----------------------------------------------------------------------
  // Get mem interface
  //----------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return m_prev.memreq(); }
    xmem::MemRespStream& memresp() const { return m_prev.memresp(); }

    static size_t size() {
      return 2*PTR_SIZE + MemValue<T>::size();
    }
  };

};

#endif /* POLYDSU_LIST_LIST_PROXY_H */

