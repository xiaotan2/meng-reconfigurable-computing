//========================================================================
// tree proxies header
//========================================================================
// This file contains proxy objects for use with List

#ifndef POLYDSU_TREE_TREE_PROXY_H
#define POLYDSU_TREE_TREE_PROXY_H

#include <stdlib.h>
#include <stdio.h>

#include "xmem/MemProxy.h"

//------------------------------------------------------------------------
// This should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename T>
class _Node {
  Node_ *m_parent;
  Node_ *m_first_child,  *m_last_child;
  Node_ *m_prev_sib,     *m_next_sib;
  T m_value;
};

namespace xmem {
  //----------------------------------------------------------------------
  // Tree MemValue
  //----------------------------------------------------------------------
  template<typename T>
  class MemValue< _Node<T> > {
    public:
      MemValue< MemPointer< _Node<T> > > m_parent;
      MemValue< MemPointer< _Node<T> > > m_first_child;
      MemValue< MemPointer< _Node<T> > > m_last_child;
      MemValue< MemPointer< _Node<T> > > m_prev_sib;
      MemValue< MemPointer< _Node<T> > > m_next_sib;
      MemValue<T> m_value;

  //----------------------------------------------------------------------
  // Constructors
  //----------------------------------------------------------------------
    MemValue( xmem::Address base_ptr,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_parent      ( base_ptr, memreq, memresp ),
        m_first_child ( base_ptr+PTR_SIZE, memreq, memresp ),
        m_last_child  ( base_ptr+2*PTR_SIZE, memreq, memresp ),
        m_prev_sib    ( base_ptr+3*PTR_SIZE, memreq, memresp ),
        m_next_sib    ( base_ptr+4*PTR_SIZE, memreq, memresp ),
        m_value       ( base_ptr+5*PTR_SIZE )
    {}

  //----------------------------------------------------------------------
  // Get/Set xmem::Address
  //----------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_parent.set_addr( base_ptr ),
      m_first_child.set_addr( base_ptr+PTR_SIZE ),
      m_last_child.set_addr( base_ptr+2*PTR_SIZE ),
      m_prev_sib.set_addr( base_ptr+3*PTR_SIZE ),
      m_next_sib.set_addr( base_ptr+4*PTR_SIZE ),
      m_value.set_addr( addr+5*PTR_SIZE );
    }

    xmem::Address get_addr() const { return m_parent.get_addr(); }
    xmem::MemReqStream&  memreq()  const { return m_parent.memreq(); }
    xmem::MemRespStream& memresp() const { return m_parent.memresp(); }
    static size_t size() {
      return 5*PTR_SIZE + MemValue<T>::size();
    }

  };

}; // end namespace xmem

#endif /* POLYDSU_TREE_TREE_PROXY_H */
