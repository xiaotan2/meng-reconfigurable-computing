//========================================================================
// PolyHS list header
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : September 17, 2014
// Project : Polymorphic Hardware Specialization
//
// Linked list container implementation inspired from C++ STL.

#ifndef POLYDSU_LIST_LIST_H
#define POLYDSU_LIST_LIST_H

#include <cstddef>
#include <iostream>
#include <stdlib.h>
#include <stdio.h>

#include "polydsu_list/ListProxy.h"

//------------------------------------------------------------------------
// PolyHS list container
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
class list {
  public:
    typedef size_t                              size_type;
    typedef xmem::MemValue< _NodeType<T> >      node_type;
    typedef xmem::MemPointer< _NodeType<T> >    node_ptr;

  public:
    // These template structs let us use a single class for iterator
    // and const_iterator. We can choose between them using a bool.
    // The structs let us change typedefs based on the bool value.
    // http://www.drdobbs.com/the-standard-librarian-defining-iterato/184401331?pgno=1
    template <bool flag, class IsTrue, class IsFalse>
    struct choose;

    template <class IsTrue, class IsFalse>
    struct choose<true, IsTrue, IsFalse> {
      typedef IsTrue type;
    };

    template <class IsTrue, class IsFalse>
    struct choose<false, IsTrue, IsFalse> {
      typedef IsFalse type;
    };

    //--------------------------------------------------------------------
    // Iterator Class
    //--------------------------------------------------------------------
    template<typename T2, bool isconst=false>
    class _iterator
    {
    public:
      typedef std::bidirectional_iterator_tag   iterator_category;
      typedef ptrdiff_t                         difference_type;
      typedef xmem::MemValue<T2>                value_type;
      typedef xmem::MemPointer< _NodeType<T2> > pointer;
      typedef typename choose<isconst, const value_type, value_type>::type
                                                reference;
    public:
      pointer p;

    public:
      // default constructor
      _iterator( xmem::Opaque opq,
                 xmem::MemReqStream& memreq,
                 xmem::MemRespStream& memresp )
        : p(0, opq, memreq, memresp)
      {}

      // addr constructor
      _iterator ( xmem::Address addr, xmem::Opaque opq,
                  xmem::MemReqStream& memreq,
                  xmem::MemRespStream& memresp )
        : p(addr, opq, memreq, memresp )
      {}

      // pointer constructor
      _iterator ( pointer ptr )
        : p(ptr)
      {}

      // copy constructor
      _iterator ( const _iterator<T2, false>& it )
        : p(it.p)
      {}

      _iterator& operator= (const _iterator& rhs) {p=rhs.p; return *this;}
      _iterator& operator++() {p=p->m_next; return *this;}
      _iterator  operator++(int) {_iterator tmp(*this); operator++(); return tmp;}
      _iterator& operator--() {p=p->m_prev; return *this;}
      _iterator  operator--(int) {_iterator tmp(*this); operator--(); return tmp;}

      bool operator==(const _iterator& rhs) const {return p==rhs.p;}
      bool operator!=(const _iterator& rhs) const {return !(*this==rhs);}

      reference operator*() const {return p->m_value;}

      pointer get_ptr() { return p; }
    };
    //--------------------------------------------------------------------
    // End iterator
    //--------------------------------------------------------------------

    typedef _iterator< T,false> iterator;
    typedef _iterator< T,true>  const_iterator;

  private:
    node_ptr m_node;

    node_ptr get_node( const T& val );
    void put_node( node_ptr p );

  public:
    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    list( xmem::Address header_addr,  xmem::Opaque opq, 
          xmem::MemReqStream& memreq, xmem::MemRespStream& memresp );
    //list( xmem::Opaque opq, 
    //      xmem::MemReqStream& memreq, xmem::MemRespStream& memresp );
    //list( const list& x );

    //--------------------------------------------------------------------
    // Destructor
    //--------------------------------------------------------------------
    ~list();

    //--------------------------------------------------------------------
    // size methods
    //--------------------------------------------------------------------
    size_type size() const;
    bool empty() const;

    //--------------------------------------------------------------------
    // Iterator methods
    //--------------------------------------------------------------------
    const_iterator begin() const;
    const_iterator end() const;
    const_iterator cbegin() const;
    const_iterator cend() const;
    iterator begin();
    iterator end();

    //--------------------------------------------------------------------
    // Mutators
    //--------------------------------------------------------------------
    iterator push_front( node_ptr new_node );
    void pop_front();
    iterator push_back( node_ptr new_node );
    void pop_back();
    iterator insert( const_iterator pos, node_ptr new_node );
    iterator erase( const_iterator pos );
    iterator erase( const_iterator first, const_iterator last );
    void swap (list& x);
    void clear();

    //--------------------------------------------------------------------
    // Algorithms
    //--------------------------------------------------------------------
    void splice( const_iterator pos, list& x);
    void splice( const_iterator pos, list& x, const_iterator i );
    void splice( const_iterator pos, list& x, const_iterator first, const_iterator last );
    void remove( const T& val );
    void sort();
};

// Include the implementation files which contains implementations for the
// template functions
#include "polydsu_list/List.inl"
#endif /* POLYDSU_LIST_LIST */

