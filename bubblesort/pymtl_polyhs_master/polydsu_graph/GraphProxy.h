//========================================================================
// graph proxies header
//========================================================================
// This file contains proxy objects for use with List

#ifndef POLYDSU_GRAPH_GRAPH_PROXY_H
#define POLYDSU_GRAPH_GRAPH_PROXY_H

#include <stdlib.h>
#include <stdio.h>

#include "xmem/MemProxy.h"

//------------------------------------------------------------------------
// These types should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename T>
class _Vertex {
  int m_label;
  T   m_data;

  _Vertex* m_prev;
  _Vertex* m_next;
};

template<typename T>
class _Edge {
  _Vertex<T>* src;
  _Vertex<T>* dst;

  int m_weight;
  
  _Edge* m_prev;
  _Edge* m_next;
};


namespace xmem {
  //----------------------------------------------------------------------
  // Vertex MemValue
  //----------------------------------------------------------------------
  template<typename T>
  class MemValue< _Vertex<T> > {
    public:
      MemValue<int> m_label;
      MemValue<T>   m_data;
      MemValue< MemPointer< _Vertex<T> > > m_prev;
      MemValue< MemPointer< _Vertex<T> > > m_next;

    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_label( base_ptr, opq, memreq, memresp ),
        m_data ( base_ptr+sizeof(int), opq, memreq, memresp ),
        m_prev ( base_ptr+sizeof(int)+sizeof(T), opq, memreq, memresp ),
        m_next ( base_ptr+sizeof(int)+sizeof(T)+PTR_SIZE, opq, memreq, memresp )
    {}

    //--------------------------------------------------------------------
    // Get/Set Address
    //--------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_label.set_addr( addr );
      m_data.set_addr ( addr+sizeof(int) );
      m_prev.set_addr ( addr+sizeof(int)+sizeof(T) );
      m_next.set_addr ( addr+sizeof(int)+sizeof(T)+PTR_SIZE );
    }

    xmem::Address get_addr() const { return m_label.get_addr(); }
  
    //--------------------------------------------------------------------
    // Get/Set Opaque
    //--------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      m_label.set_opq( opq );
      m_data.set_opq ( opq );
      m_prev.set_opq ( opq );
      m_next.set_opq ( opq );
    }

    xmem::Opaque get_opq() const { return m_label.get_opq(); }

    //--------------------------------------------------------------------
    // Get mem interface
    //--------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return m_label.memreq(); }
    xmem::MemRespStream& memresp() const { return m_label.memresp(); }

    static size_t size() {
      return 2*PTR_SIZE + MemValue<int>::size() + MemValue<T>::size();
    }
  };


  //----------------------------------------------------------------------
  // Edge MemValue
  //----------------------------------------------------------------------
  template<typename T>
  class MemValue< _Edge<T> > {
    public:
      MemValue< MemPointer< _Vertex<T> > > src;
      MemValue< MemPointer< _Vertex<T> > > dst;
      MemValue<int>   m_weight;
      MemValue< MemPointer< _Edge<T> > > m_prev;
      MemValue< MemPointer< _Edge<T> > > m_next;

    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : src( base_ptr, opq, memreq, memresp ),
        dst( base_ptr+PTR_SIZE, opq, memreq, memresp ),
        m_weight( base_ptr+2*PTR_SIZE, opq, memreq, memresp ),
        m_prev( base_ptr+3*PTR_SIZE, opq, memreq, memresp ),
        m_next( base_ptr+4*PTR_SIZE, opq, memreq, memresp )
    {}

    //--------------------------------------------------------------------
    // Get/Set Address
    //--------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      src.set_addr    ( addr );
      dst.set_addr    ( addr+PTR_SIZE );
      m_weight.set_addr ( addr+2*PTR_SIZE );
      m_next.set_addr   ( addr+3*PTR_SIZE );
      m_prev.set_addr   ( addr+4*PTR_SIZE );
    }

    xmem::Address get_addr() const { return src.get_addr(); }
  
    //--------------------------------------------------------------------
    // Get/Set Opaque
    //--------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      src.set_opq ( opq );
      dst.set_opq ( opq );
      m_weight.set_opq( opq );
      m_next.set_opq( opq );
      m_prev.set_opq( opq );
    }

    xmem::Opaque get_opq() const { return src.get_opq(); }

    //--------------------------------------------------------------------
    // Get mem interface
    //--------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return src.memreq(); }
    xmem::MemRespStream& memresp() const { return src.memresp(); }

    static size_t size() {
      return 4*PTR_SIZE + MemValue<int>::size();
    }
  };

};

#endif /* POLYDSU_GRAPH_GRAPH_PROXY_H */
