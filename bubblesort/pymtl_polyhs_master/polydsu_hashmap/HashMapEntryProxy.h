//========================================================================
// HasMapEntryProxy.h
//========================================================================
// This file contains the proxy object for use with the hash map

#ifndef POLYDSU_HASH_MAP_HASH_MAP_ENTRY_PROXY_H
#define POLYDSU_HASH_MAP_HASH_MAP_ENTRY_PROXY_H

#include "xmem/MemProxy.h"

//------------------------------------------------------------------------
// This should never be actually used in code, it exists
// as a type to specialize MemValue on
//------------------------------------------------------------------------
template<typename T>
class HashMapEntry {
  HashMapEntry* m_next;
  T             m_key;
  T             m_value;
};

namespace xmem {
  //----------------------------------------------------------------------
  // HaspMapEntry MemValue
  //----------------------------------------------------------------------
  template<typename T>
  class MemValue< HashMapEntry<T> > {
    public:
      MemValue< MemPointer< HashMapEntry<T> > > m_next;
      MemValue<T>                               m_key;
      MemValue<T>                               m_value;

  //----------------------------------------------------------------------
  // Constructors
  //----------------------------------------------------------------------
    MemValue( xmem::Address base_ptr, xmem::Opaque opq,
              xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
      : m_next ( base_ptr, opq, memreq, memresp ),
        m_key  ( base_ptr+PTR_SIZE, opq, memreq, memresp ),
        m_value( base_ptr+PTR_SIZE+PTR_SIZE, opq, memreq, memresp )
    {}

  //----------------------------------------------------------------------
  // Get/Set Address
  //----------------------------------------------------------------------
    void set_addr( const xmem::Address addr ) {
      m_next.set_addr ( addr );
      m_key.set_addr ( addr+PTR_SIZE );
      m_value.set_addr( addr+PTR_SIZE+PTR_SIZE );
    }

    xmem::Address get_addr() const { return m_next.get_addr(); }

  //----------------------------------------------------------------------
  // Get/Set Opaque
  //----------------------------------------------------------------------
    void set_opq( const xmem::Opaque opq ) {
      m_next.set_opq ( opq );
      m_key.set_opq ( opq );
      m_value.set_opq( opq );
    }

    xmem::Opaque get_opq() const { return m_next.get_opq(); }

  //----------------------------------------------------------------------
  // Get mem interface
  //----------------------------------------------------------------------
    xmem::MemReqStream&  memreq()  const { return m_next.memreq(); }
    xmem::MemRespStream& memresp() const { return m_next.memresp(); }

    static size_t size() {
      return 2*PTR_SIZE + MemValue<T>::size();
    }
  };


  //----------------------------------------------------------------------
  // HashMapEntryPtr
  //----------------------------------------------------------------------

  typedef xmem::MemPointer< HashMapEntry<int> > HashMapEntryPtr;

}

#endif /* POLYDSU_HASH_MAP_HASH_MAP_ENTRY_PROXY_H */


