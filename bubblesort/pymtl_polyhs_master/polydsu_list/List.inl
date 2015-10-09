//========================================================================
// PolyHS list inline methods
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : September 17, 2014
// Project : Polymorphic Hardware Specialization
//
// Linked list container implementation inspired from C++ STL.

//------------------------------------------------------------------------
// Memory Allocation/Deallocation
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::node_ptr list<_NodeType,T>::get_node( const T& val ) {
  node_ptr node( 0,
                 m_node.get_opq(),
                 m_node.memreq(), m_node.memresp() );
  return node;
}

template<template<typename M> class _NodeType, typename T>
void list<_NodeType,T>::put_node( node_ptr p ) {
}

//------------------------------------------------------------------------
// Constructors
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
list<_NodeType,T>::list( xmem::Address header_addr,  xmem::Opaque opq, 
               xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
  : m_node( node_ptr( header_addr, opq, memreq, memresp ) )
{
}

//------------------------------------------------------------------------
// Destructor
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
list<_NodeType,T>::~list() {
}

//------------------------------------------------------------------------
// size methods
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::size_type list<_NodeType,T>::size() const {
  size_type tmp = 0;
  for (const_iterator i = begin(); i != end(); ++i)
    tmp++;
  return tmp;
}

template<template<typename M> class _NodeType, typename T>
inline bool list<_NodeType,T>::empty() const {
  return size() == 0;
}

//------------------------------------------------------------------------
// Iterator methods
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::const_iterator list<_NodeType,T>::begin() const {
  return const_iterator(m_node->m_next);
}

template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::const_iterator list<_NodeType,T>::end() const {
  return const_iterator(m_node);
}

template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::const_iterator list<_NodeType,T>::cbegin() const {
  return const_iterator(m_node->m_next);
}

template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::const_iterator list<_NodeType,T>::cend() const {
  return const_iterator(m_node);
}

template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::iterator list<_NodeType,T>::begin() {
  return iterator(m_node->m_next);
}

template<template<typename M> class _NodeType, typename T>
inline typename list<_NodeType,T>::iterator list<_NodeType,T>::end() {
  return iterator(m_node);
}

//------------------------------------------------------------------------
// Push/Pop front
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::iterator
list<_NodeType,T>::push_front( node_ptr new_node ) {
  return insert (begin(), new_node);
}

template<template<typename M> class _NodeType, typename T>
inline void list<_NodeType,T>::pop_front() {
  erase (begin());
}

//------------------------------------------------------------------------
// Push/Pop back
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::iterator
list<_NodeType,T>::push_back( node_ptr new_node ) {
  return insert (end(), new_node);
}

template<template<typename M> class _NodeType, typename T>
inline void list<_NodeType,T>::pop_back() {
  iterator tmp = end();
  erase (--tmp);
}

//------------------------------------------------------------------------
// Insert
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::iterator list<_NodeType,T>::insert( const_iterator pos, node_ptr new_node ) {
  new_node->m_next = pos.p;
  new_node->m_prev = pos.p->m_prev;

  pos.p->m_prev->m_next = new_node;
  pos.p->m_prev = new_node;
  return iterator(new_node);
}

//------------------------------------------------------------------------
// Erase
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::iterator list<_NodeType,T>::erase( const_iterator pos) {
  node_ptr prev_node = pos.p->m_prev;
  node_ptr next_node = pos.p->m_next;
  prev_node->m_next = next_node;
  next_node->m_prev = prev_node;
  put_node( pos.p );
  return iterator(next_node);
}

template<template<typename M> class _NodeType, typename T>
typename list<_NodeType,T>::iterator list<_NodeType,T>::erase( const_iterator first, const_iterator last ) {
  for (; first != last; ) {
    first = erase(first);
  }
  return iterator(last.p);
}

//------------------------------------------------------------------------
// Swap
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
void list<_NodeType,T>::swap( list& x ) {
  node_ptr tmp = m_node;
  m_node = x.m_node;
  x.m_node = tmp;
}

//------------------------------------------------------------------------
// Clear
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
inline void list<_NodeType,T>::clear() {
  erase( begin(), end() );
}

//------------------------------------------------------------------------
// Splice
//------------------------------------------------------------------------
template<template<typename M> class _NodeType, typename T>
void list<_NodeType,T>::splice( const_iterator pos, list& x ) {
  splice( pos, x, x.begin(), x.end() );
}

template<template<typename M> class _NodeType, typename T>
void list<_NodeType,T>::splice( const_iterator pos, list& x, const_iterator first, const_iterator last ) {
  if (first == last) return;
  last.p->m_prev->m_next = pos.p;
  first.p->m_prev->m_next = last.p;
  pos.p->m_prev->m_next = first.p;

  node_ptr tmp = last.p->m_prev;
  last.p->m_prev = first.p->m_prev;
  first.p->m_prev = pos.p->m_prev;
  pos.p->m_prev = tmp;
}

template<template<typename M> class _NodeType, typename T>
void list<_NodeType,T>::splice( const_iterator pos, list& x, const_iterator i ) {
  const_iterator i1 = i;
  splice( pos, x, i, ++i1 );
}

