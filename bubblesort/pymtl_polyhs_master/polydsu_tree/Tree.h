//========================================================================
//      STL-like templated tree class.
//
// Copyright (C) 2001-2014 Kasper Peeters <kasper@phi-sci.com>
// Distributed under the GNU General Public License version 3.
//
// Special permission to use tree.hh under the conditions of a 
// different license can be requested from the author.
//========================================================================

/** \mainpage tree.hh
  \author   Kasper Peeters
  \version  3.1
  \date     06-May-2015
  \see      http://tree.phi-sci.com/
  \see      http://tree.phi-sci.com/ChangeLog

  The tree.hh library for C++ provides an STL-like container class
  for n-ary trees, templated over the data stored at the
  nodes. Various types of iterators are provided (post-order,
  pre-order, and others). Where possible the access methods are
  compatible with the STL or alternative algorithms are
  available. 
*/


#ifndef POLYDSU_TREE_TREE_H
#define POLYDSU_TREE_TREE_H

#include <cassert>
#include <iterator>
#include <algorithm>
#include <cstddef>

#include "polydsu_tree/TreeProxy.h"

namespace polydsu_tree {

  template <class T>
  class tree {
    protected:
      typedef MemValue< _Node<T> >    Node;
      typedef MemPointer< _Node<T> >  NodePtr;
    public:

      /// Value of the data stored at a node.
      typedef T value_type;

      class iterator_base;
      class pre_order_iterator;
      class post_order_iterator;
      class sibling_iterator;
      class leaf_iterator;

      tree(xmem::MemReqStream&, xmem::MemRespStream&);
      tree(const T&, xmem::MemReqStream&, xmem::MemRespStream&);
      tree(const iterator_base&, xmem::MemReqStream&, xmem::MemRespStream&);
      tree(const tree<T>&);
      ~tree();
      tree<T>& operator=(const tree<T>&);             // copy assignment

    private:

      NodePtr get_node_init(xmem::MemReqStream&, xmem::MemRespStream&);
      NodePtr get_node();
      void put_node( NodePtr p );

    public:

      /// Base class for iterators, only pointers stored, no traversal logic.
      class iterator_base {
        public:
          typedef T                               value_type;
          typedef T*                              pointer;
          typedef T&                              reference;
          typedef size_t                          size_type;
          typedef ptrdiff_t                       difference_type;
          typedef std::bidirectional_iterator_tag iterator_category;

          iterator_base();
          iterator_base(NodePtr);

          T& operator* () const;
          T* operator->() const;

          /// When called, the next increment/decrement skips children of this node.
          void         skip_children();
          void         skip_children(bool skip);
          /// Number of children of the node pointed to by the iterator.
          unsigned int number_of_children() const;

          sibling_iterator begin() const;
          sibling_iterator end() const;

          NodePtr node;
        protected:
          bool skip_current_children_;
      };

      /// Depth-first iterator, first accessing the node, then its children.
      class pre_order_iterator : public iterator_base { 
        public:
          pre_order_iterator();
          pre_order_iterator(NodePtr);
          pre_order_iterator(const iterator_base&);
          pre_order_iterator(const sibling_iterator&);

          bool    operator==(const pre_order_iterator&) const;
          bool    operator!=(const pre_order_iterator&) const;
          pre_order_iterator&  operator++();
          pre_order_iterator&  operator--();
          pre_order_iterator   operator++(int);
          pre_order_iterator   operator--(int);
          pre_order_iterator&  operator+=(unsigned int);
          pre_order_iterator&  operator-=(unsigned int);

          pre_order_iterator&  next_skip_children();
      };

      /// Depth-first iterator, first accessing the children, then the node itself.
      class post_order_iterator : public iterator_base {
        public:
          post_order_iterator();
          post_order_iterator(NodePtr);
          post_order_iterator(const iterator_base&);
          post_order_iterator(const sibling_iterator&);

          bool    operator==(const post_order_iterator&) const;
          bool    operator!=(const post_order_iterator&) const;
          post_order_iterator&  operator++();
          post_order_iterator&  operator--();
          post_order_iterator   operator++(int);
          post_order_iterator   operator--(int);
          post_order_iterator&  operator+=(unsigned int);
          post_order_iterator&  operator-=(unsigned int);

          /// Set iterator to the first child as deep as possible down the tree.
          void descend_all();
      };

      /// The default iterator types throughout the tree class.
      typedef pre_order_iterator            iterator;

      /// Iterator which traverses only the nodes which are siblings of each other.
      class sibling_iterator : public iterator_base {
        public:
          sibling_iterator();
          sibling_iterator(NodePtr);
          sibling_iterator(const sibling_iterator&);
          sibling_iterator(const iterator_base&);

          bool    operator==(const sibling_iterator&) const;
          bool    operator!=(const sibling_iterator&) const;
          sibling_iterator&  operator++();
          sibling_iterator&  operator--();
          sibling_iterator   operator++(int);
          sibling_iterator   operator--(int);
          sibling_iterator&  operator+=(unsigned int);
          sibling_iterator&  operator-=(unsigned int);

          NodePtr range_first() const;
          NodePtr range_last() const;
          NodePtr parent_;
        private:
          void set_parent_();
      };

      /// Iterator which traverses only the leaves.
      class leaf_iterator : public iterator_base {
        public:
          leaf_iterator();
          leaf_iterator(NodePtr , NodePtr top=0);
          leaf_iterator(const sibling_iterator&);
          leaf_iterator(const iterator_base&);

          bool    operator==(const leaf_iterator&) const;
          bool    operator!=(const leaf_iterator&) const;
          leaf_iterator&  operator++();
          leaf_iterator&  operator--();
          leaf_iterator   operator++(int);
          leaf_iterator   operator--(int);
          leaf_iterator&  operator+=(unsigned int);
          leaf_iterator&  operator-=(unsigned int);
        private:
          NodePtr top_node;
      };

      /// Return iterator to the beginning of the tree.
      inline pre_order_iterator   begin() const;
      /// Return iterator to the end of the tree.
      inline pre_order_iterator   end() const;
      /// Return post-order iterator to the beginning of the tree.
      post_order_iterator  begin_post() const;
      /// Return post-order end iterator of the tree.
      post_order_iterator  end_post() const;
      /// Return sibling iterator to the first child of given node.
      sibling_iterator     begin(const iterator_base&) const;
      /// Return sibling end iterator for children of given node.
      sibling_iterator     end(const iterator_base&) const;
      /// Return leaf iterator to the first leaf of the tree.
      leaf_iterator   begin_leaf() const;
      /// Return leaf end iterator for entire tree.
      leaf_iterator   end_leaf() const;
      /// Return leaf iterator to the first leaf of the subtree at the given node.
      leaf_iterator   begin_leaf(const iterator_base& top) const;
      /// Return leaf end iterator for the subtree at the given node.
      leaf_iterator   end_leaf(const iterator_base& top) const;

      /// Return iterator to the parent of a node.
      template<typename iter> static iter parent(iter);
      /// Return iterator to the previous sibling of a node.
      template<typename iter> static iter previous_sibling(iter);
      /// Return iterator to the next sibling of a node.
      template<typename iter> static iter next_sibling(iter);

      /// Erase all nodes of the tree.
      void     clear();
      /// Erase element at position pointed to by iterator, return incremented iterator.
      template<typename iter> iter erase(iter);
      /// Erase all children of the node pointed to by iterator.
      void     erase_children(const iterator_base&);

      /// Short-hand to insert topmost node in otherwise empty tree.
      pre_order_iterator set_head(const T& x);

      /// Insert node as last/first child of node pointed to by position.
      template<typename iter> iter append_child(iter position, const T& x);
      template<typename iter> iter prepend_child(iter position, const T& x);

      /// Insert node as previous sibling of node pointed to by position.
      template<typename iter> iter insert(iter position, const T& x);
      /// Specialisation of previous member.
      sibling_iterator insert(sibling_iterator position, const T& x);
      /// Insert node as next sibling of node pointed to by position.
      template<typename iter> iter insert_after(iter position, const T& x);

      /// Replace node at 'position' with other node (keeping same children); 'position' becomes invalid.
      template<typename iter> iter replace(iter position, const T& x);
      /// Replace node at 'position' with subtree starting at 'from' (do not erase subtree at 'from'); see above.
      template<typename iter> iter replace(iter position, const iterator_base& from);

      /// Move 'source' node (plus its children) to become the next sibling of 'target'.
      template<typename iter> iter move_after(iter target, iter source);
      /// Move 'source' node (plus its children) to become the previous sibling of 'target'.
      template<typename iter> iter move_before(iter target, iter source);

      /// Extract the subtree starting at the indicated node, removing it from original tree.
      tree                         move_out(iterator);
      /// Inverse of move_out: inserts the given tree as previous sibling of indicated node
      /// via a move, that is, the given tree becomes empty. Returns iterator to the top node.
      template<typename iter> iter move_in(iter, tree&);

      /// Count the total number of nodes.
      size_t   size() const;
      /// Count the total number of nodes below the indicated node (plus one).
      size_t   size(const iterator_base&) const;
      /// Check if tree is empty.
      bool     empty() const;
      /// Compute the depth to the root or to a fixed other iterator.
      static int depth(const iterator_base&);
      static int depth(const iterator_base&, const iterator_base&);
      /// Determine the maximal depth of the tree. An empty tree has max_depth=-1.
      int      max_depth() const;
      /// Determine the maximal depth of the tree with top node at the given position.
      int      max_depth(const iterator_base&) const;
      /// Count the number of children of node at position.
      static unsigned int number_of_children(const iterator_base&);
      /// Count the number of siblings (left and right) of node at iterator. Total nodes at this level is +1.
      unsigned int number_of_siblings(const iterator_base&) const;
      /// Determine whether the iterator is an 'end' iterator and thus not actually pointing to a node.
      bool     is_valid(const iterator_base&) const;

      /// Determine the index of a node in the range of siblings to which it belongs.
      unsigned int index(sibling_iterator it) const;
      /// Inverse of 'index': return the n-th child of the node at position.
      static sibling_iterator child(const iterator_base& position, unsigned int);
      /// Return iterator to the sibling indicated by index
      sibling_iterator sibling(const iterator_base& position, unsigned int);                                  

      /// For debugging only: verify internal consistency by inspecting all pointers in the tree
      /// (which will also trigger a valgrind error in case something got corrupted).
      void debug_verify_consistency() const;


      NodePtr head, feet;    // head/feet are always dummy; if an iterator points to them it is invalid
    private:
      void root_initialise_();
      void copy_(const tree<T>& other);
  };

  //----------------------------------------------------------------------
  // Memory Allocation/Deallocation
  //----------------------------------------------------------------------

  NodePtr get_node_init(
      xmem::MemReqStream& memreq,
      xmem::MemRespStream& memresp
  ){
    xmem::Address ptr = (xmem::Address)malloc( Node::size() );
    return NodePtr( ptr, memreq, memresp );
  }

  NodePtr get_node() {
    return get_node_init( head.memreq(), head.memresp() );
  }

  void put_node( NodePtr p ) {
    free( p.get_addr() );
  }

  //----------------------------------------------------------------------
  // Constructors
  //----------------------------------------------------------------------

  template <class T>
  tree<T>::tree( xmem::MemReqStream& memreq, xmem::MemRespStream& memresp )
    : head( get_node_init(memreq, memresp) ),
      feet( get_node_init(memreq, memresp) )
  {
    root_initialise_();
  }

  template <class T>
  tree<T>::tree(const T& x) 
    : head( get_node_init(memreq, memresp) ),
      feet( get_node_init(memreq, memresp) )
  {
    root_initialise_();
    set_head(x);
  }

  template <class T>
  tree<T>::tree(const iterator_base& other)
    : head( get_node_init(memreq, memresp) ),
      feet( get_node_init(memreq, memresp) )
  {
    root_initialise_();
    set_head((*other));
    replace(begin(), other);
  }
  
  template <class T>
  tree<T>::tree(const tree<T>& other)
    : head( get_node_init(memreq, memresp) ),
      feet( get_node_init(memreq, memresp) )
  {
    root_initialise_();
    copy_(other);
  }

  //----------------------------------------------------------------------
  // Destructors
  //----------------------------------------------------------------------
  
  template <class T>
  tree<T>::~tree()
  {
    clear();
    put_node( head );
    put_node( feet );
  }
  
  //----------------------------------------------------------------------
  // Memory Allocation/Deallocation
  //----------------------------------------------------------------------

  template <class T>
  typename tree<T>::NodePtr tree<T>::get_node_init( 
      xmem::MemReqStream& memreq,
      xmem::MemReqStream& memresp
  ){
    void* mem = (void*)malloc( MemValue< _Node<T> >::size() );
    return NodePtr( mem, memreq, memresp );
  }

  template <class T>
  typename tree<T>::NodePtr tree<T>::get_node() {
    void* mem = (void*)malloc( MemValue< _Node<T> >::size() );
    return NodePtr( mem, head.memreq(), head.memresp() );
  }
  
  template <class T>
  void tree<T>::put_node( NodePtr p ) {
    free( p.get_addr() );
  }

  //----------------------------------------------------------------------
  // 
  //----------------------------------------------------------------------
  
  template <class T>
  void tree<T>::root_initialise_() 
  { 
    head->m_parent=0;
    head->m_first_child=0;
    head->m_last_child=0;
    head->m_prev_sib=0; //head;
    head->m_next_sib=feet; //head;

    feet->m_parent=0;
    feet->m_first_child=0;
    feet->m_last_child=0;
    feet->m_prev_sib=head;
    feet->m_next_sib=0;
  }

  template <class T>
  tree<T>& tree<T>::operator=(const tree<T>& other)
  {
    if(this != &other)
      copy_(other);
    return *this;
  }

  template <class T>
  void tree<T>::copy_(const tree<T>& other) 
  {
    clear();
    pre_order_iterator it=other.begin(), to=begin();
    while(it!=other.end()) {
      to=insert(to, (*it));
      it.skip_children();
      ++it;
    }
    to=begin();
    it=other.begin();
    while(it!=other.end()) {
      to=replace(to, it);
      to.skip_children();
      it.skip_children();
      ++to;
      ++it;
    }
  }

  template <class T>
  void tree<T>::clear()
  {
    if(head)
      while(head->m_next_sib!=feet)
        erase(pre_order_iterator(head->m_next_sib));
  }

  template<class T> 
  void tree<T>::erase_children(const iterator_base& it)
  {
    //      std::cout << "erase_children " << it.node << std::endl;
    if(it.node==0) return;

    NodePtr cur=it.node->m_first_child;
    NodePtr prev(0, head.memreq(), head.memresp() );

    while(cur!=0) {
      prev=cur;
      cur=cur->m_next_sib;
      erase_children(pre_order_iterator(prev));
      put_node( prev );
    }
    it.node->m_first_child=0;
    it.node->m_last_child=0;
    //      std::cout << "exit" << std::endl;
  }

  template<class T> 
  template<class iter>
  iter tree<T>::erase(iter it)
  {
    NodePtr cur=it.node;
    assert(cur!=head);
    iter ret=it;
    ret.skip_children();
    ++ret;
    erase_children(it);
    if(cur->m_prev_sib==0) {
      cur->m_parent->m_first_child=cur->m_next_sib;
    }
    else {
      cur->m_prev_sib->m_next_sib=cur->m_next_sib;
    }
    if(cur->m_next_sib==0) {
      cur->m_parent->m_last_child=cur->m_prev_sib;
    }
    else {
      cur->m_next_sib->m_prev_sib=cur->m_prev_sib;
    }

    put_node( cur );
    return ret;
  }

  template <class T>
  typename tree<T>::pre_order_iterator tree<T>::begin() const
  {
    return pre_order_iterator(head->m_next_sib);
  }

  template <class T>
  typename tree<T>::pre_order_iterator tree<T>::end() const
  {
    return pre_order_iterator(feet);
  }

  template <class T>
  typename tree<T>::post_order_iterator tree<T>::begin_post() const
  {
    NodePtr tmp=head->m_next_sib;
    if(tmp!=feet) {
      while(tmp->m_first_child)
        tmp=tmp->m_first_child;
    }
    return post_order_iterator(tmp);
  }

  template <class T>
  typename tree<T>::post_order_iterator tree<T>::end_post() const
  {
    return post_order_iterator(feet);
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::begin(const iterator_base& pos) const
  {
    assert(pos.node!=0);
    if(pos.node->m_first_child==0) {
      return end(pos);
    }
    return pos.node->m_first_child;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::end(const iterator_base& pos) const
  {
    sibling_iterator ret(0);
    ret.m_parent_=pos.node;
    return ret;
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::begin_leaf() const
  {
    NodePtr tmp=head->m_next_sib;
    if(tmp!=feet) {
      while(tmp->m_first_child)
        tmp=tmp->m_first_child;
    }
    return leaf_iterator(tmp);
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::end_leaf() const
  {
    return leaf_iterator(feet);
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::begin_leaf(const iterator_base& top) const
  {
    NodePtr tmp=top.node;
    while(tmp->m_first_child)
      tmp=tmp->m_first_child;
    return leaf_iterator(tmp, top.node);
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::end_leaf(const iterator_base& top) const
  {
    return leaf_iterator(top.node, top.node);
  }

  template <class T>
  template <typename iter> iter tree<T>::m_parent(iter position) 
  {
    assert(position.node!=0);
    return iter(position.node->m_parent);
  }

  template <class T>
  template <typename iter> iter tree<T>::previous_sibling(iter position) 
  {
    assert(position.node!=0);
    iter ret(position);
    ret.node=position.node->m_prev_sib;
    return ret;
  }

  template <class T>
  template <typename iter> iter tree<T>::next_sibling(iter position) 
  {
    assert(position.node!=0);
    iter ret(position);
    ret.node=position.node->m_next_sib;
    return ret;
  }

  template <class T>
  template <class iter> iter tree<T>::append_child(iter position, const T& x)
  {
    // If your program fails here you probably used 'append_child' to add the top
    // node to an empty tree. From version 1.45 the top element should be added
    // using 'insert'. See the documentation for further information, and sorry about
    // the API change.
    assert(position.node!=head);
    assert(position.node!=feet);
    assert(position.node);

    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;

    tmp->m_parent=position.node;
    if(position.node->m_last_child!=0) {
      position.node->m_last_child->m_next_sib=tmp;
    }
    else {
      position.node->m_first_child=tmp;
    }
    tmp->m_prev_sib=position.node->m_last_child;
    position.node->m_last_child=tmp;
    tmp->m_next_sib=0;
    return tmp;
  }

  template <class T>
  template <class iter> iter tree<T>::prepend_child(iter position, const T& x)
  {
    assert(position.node!=head);
    assert(position.node!=feet);
    assert(position.node);

    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;

    tmp->m_parent=position.node;
    if(position.node->m_first_child!=0) {
      position.node->m_first_child->m_prev_sib=tmp;
    }
    else {
      position.node->m_last_child=tmp;
    }
    tmp->m_next_sib=position.node->m_first_child;
    position.node->m_first_child=tmp;
    tmp->m_prev_sib=0;
    return tmp;
  }

  template <class T>
  typename tree<T>::pre_order_iterator tree<T>::set_head(const T& x)
  {
    assert(head->m_next_sib==feet);
    return insert(iterator(feet), x);
  }

  template <class T>
  template <class iter> iter tree<T>::insert(iter position, const T& x)
  {
    if(position.node==0) {
      position.node=feet; // Backward compatibility: when calling insert on a null node,
      // insert before the feet.
    }
    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;

    tmp->m_parent=position.node->m_parent;
    tmp->m_next_sib=position.node;
    tmp->m_prev_sib=position.node->m_prev_sib;
    position.node->m_prev_sib=tmp;

    if(tmp->m_prev_sib==0) {
      if(tmp->m_parent) // when inserting nodes at the head, there is no parent
        tmp->m_parent->m_first_child=tmp;
    }
    else
      tmp->m_prev_sib->m_next_sib=tmp;
    return tmp;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::insert(sibling_iterator position, const T& x)
  {
    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;

    tmp->m_next_sib=position.node;
    if(position.node==0) { // iterator points to end of a subtree
      tmp->m_parent=position.parent_;
      tmp->m_prev_sib=position.range_last();
      tmp->m_parent->m_last_child=tmp;
    }
    else {
      tmp->m_parent=position.node->m_parent;
      tmp->m_prev_sib=position.node->m_prev_sib;
      position.node->m_prev_sib=tmp;
    }

    if(tmp->m_prev_sib==0) {
      if(tmp->m_parent) // when inserting nodes at the head, there is no parent
        tmp->m_parent->m_first_child=tmp;
    }
    else
      tmp->m_prev_sib->m_next_sib=tmp;
    return tmp;
  }

  template <class T>
  template <class iter> iter tree<T>::insert_after(iter position, const T& x)
  {
    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;

    tmp->m_parent=position.node->m_parent;
    tmp->m_prev_sib=position.node;
    tmp->m_next_sib=position.node->m_next_sib;
    position.node->m_next_sib=tmp;

    if(tmp->m_next_sib==0) {
      if(tmp->m_parent) // when inserting nodes at the head, there is no parent
        tmp->m_parent->m_last_child=tmp;
    }
    else {
      tmp->m_next_sib->m_prev_sib=tmp;
    }
    return tmp;
  }

  template <class T>
  template <class iter> iter tree<T>::replace(iter position, const T& x)
  {
    position.node->m_value=x;
    return position;
  }

  template <class T>
  template <class iter> iter tree<T>::replace(iter position, const iterator_base& from)
  {
    assert(position.node!=head);
    NodePtr current_from=from.node;
    NodePtr start_from=from.node;
    NodePtr current_to  =position.node;

    // replace the node at position with head of the replacement tree at from
    erase_children(position);       
    NodePtr tmp = get_node();
    tmp->m_first_child=0;
    tmp->m_last_child=0;
    if(current_to->m_prev_sib==0) {
      if(current_to->m_parent!=0)
        current_to->m_parent->m_first_child=tmp;
    }
    else {
      current_to->m_prev_sib->m_next_sib=tmp;
    }
    tmp->m_prev_sib=current_to->m_prev_sib;
    if(current_to->m_next_sib==0) {
      if(current_to->m_parent!=0)
        current_to->m_parent->m_last_child=tmp;
    }
    else {
      current_to->m_next_sib->m_prev_sib=tmp;
    }
    tmp->m_next_sib=current_to->m_next_sib;
    tmp->m_parent=current_to->m_parent;
    put_node( current_to );
    current_to=tmp;

    // only at this stage can we fix 'last'
    NodePtr last=from.node->m_next_sib;

    pre_order_iterator toit=tmp;
    // copy all children
    do {
      assert(current_from!=0);
      if(current_from->m_first_child != 0) {
        current_from=current_from->m_first_child;
        toit=append_child(toit, current_from->m_value);
      }
      else {
        while(current_from->m_next_sib==0 && current_from!=start_from) {
          current_from=current_from->m_parent;
          toit=parent(toit);
          assert(current_from!=0);
        }
        current_from=current_from->m_next_sib;
        if(current_from!=last) {
          toit=append_child(parent(toit), current_from->m_valum_valuee);
        }
      }
    } while(current_from!=last);

    return current_to;
  }

  template <class T>
  template <typename iter> iter tree<T>::move_after(iter target, iter source)
  {
    NodePtr dst=target.node;
    NodePtr src=source.node;
    assert(dst);
    assert(src);

    if(dst==src) return source;
    if(dst->m_next_sib)
      if(dst->m_next_sib==src) // already in the right spot
        return source;

    // take src out of the tree
    if(src->m_prev_sib!=0) src->m_prev_sib->m_next_sib=src->m_next_sib;
    else                     src->m_parent->m_first_child=src->m_next_sib;
    if(src->m_next_sib!=0) src->m_next_sib->m_prev_sib=src->m_prev_sib;
    else                     src->m_parent->m_last_child=src->m_prev_sib;

    // connect it to the new point
    if(dst->m_next_sib!=0) dst->m_next_sib->m_prev_sib=src;
    else                     dst->m_parent->m_last_child=src;
    src->m_next_sib=dst->m_next_sib;
    dst->m_next_sib=src;
    src->m_prev_sib=dst;
    src->m_parent=dst->m_parent;
    return src;
  }

  template <class T>
  template <typename iter> iter tree<T>::move_before(iter target, iter source)
  {
    NodePtr dst=target.node;
    NodePtr src=source.node;
    assert(dst);
    assert(src);

    if(dst==src) return source;
    if(dst->m_prev_sib)
      if(dst->m_prev_sib==src) // already in the right spot
        return source;

    // take src out of the tree
    if(src->m_prev_sib!=0) src->m_prev_sib->m_next_sib=src->m_next_sib;
    else                     src->m_parent->m_first_child=src->m_next_sib;
    if(src->m_next_sib!=0) src->m_next_sib->m_prev_sib=src->m_prev_sib;
    else                     src->m_parent->m_last_child=src->m_prev_sib;

    // connect it to the new point
    if(dst->m_prev_sib!=0) dst->m_prev_sib->m_next_sib=src;
    else                     dst->m_parent->m_first_child=src;
    src->m_prev_sib=dst->m_prev_sib;
    dst->m_prev_sib=src;
    src->m_next_sib=dst;
    src->m_parent=dst->m_parent;
    return src;
  }

  template <class T>
  tree<T> tree<T>::move_out(iterator source)
  {
    tree ret;

    // Move source node into the 'ret' tree.
    ret.head->m_next_sib = source.node;
    ret.feet->m_prev_sib = source.node;
    source.node->m_parent=0;

    // Close the links in the current tree.
    if(source.node->m_prev_sib!=0) 
      source.node->m_prev_sib->m_next_sib = source.node->m_next_sib;

    if(source.node->m_next_sib!=0) 
      source.node->m_next_sib->m_prev_sib = source.node->m_prev_sib;

    // Fix source prev/next links.
    source.node->m_prev_sib = ret.head;
    source.node->m_next_sib = ret.feet;

    return ret; // A good compiler will move this, not copy.
  }

  template <class T>
  template<typename iter> iter tree<T>::move_in(iter loc, tree& other)
  {
    if(other.head->m_next_sib==other.feet) return loc; // other tree is empty

    NodePtr other_first_head = other.head->m_next_sib;
    NodePtr other_last_head  = other.feet->m_prev_sib;

    sibling_iterator prev(loc);
    --prev;

    prev.node->m_next_sib = other_first_head;
    loc.node->m_prev_sib  = other_last_head;
    other_first_head->m_prev_sib = prev.node;
    other_last_head->m_next_sib  = loc.node;

    // Adjust parent pointers.
    NodePtr walk=other_first_head;
    while(true) {
      walk->m_parent=loc.node->m_parent;
      if(walk==other_last_head)
        break;
      walk=walk->m_next_sib;
    }

    // Close other tree.
    other.head->m_next_sib=other.feet;
    other.feet->m_prev_sib=other.head;

    return other_first_head;
  }

  template <class T>
  size_t tree<T>::size() const
  {
    size_t i=0;
    pre_order_iterator it=begin(), eit=end();
    while(it!=eit) {
      ++i;
      ++it;
    }
    return i;
  }

  template <class T>
  size_t tree<T>::size(const iterator_base& top) const
  {
    size_t i=0;
    pre_order_iterator it=top, eit=top;
    eit.skip_children();
    ++eit;
    while(it!=eit) {
      ++i;
      ++it;
    }
    return i;
  }

  template <class T>
  bool tree<T>::empty() const
  {
    pre_order_iterator it=begin(), eit=end();
    return (it==eit);
  }

  template <class T>
  int tree<T>::depth(const iterator_base& it) 
  {
    NodePtr pos=it.node;
    assert(pos!=0);
    int ret=0;
    while(pos->m_parent!=0) {
      pos=pos->m_parent;
      ++ret;
    }
    return ret;
  }

  template <class T>
  int tree<T>::depth(const iterator_base& it, const iterator_base& root) 
  {
    NodePtr pos=it.node;
    assert(pos!=0);
    int ret=0;
    while(pos->m_parent!=0 && pos!=root.node) {
      pos=pos->m_parent;
      ++ret;
    }
    return ret;
  }

  template <class T>
  int tree<T>::max_depth() const
  {
    int maxd=-1;
    for(NodePtr it = head->m_next_sib; it!=feet; it=it->m_next_sib)
      maxd=std::max(maxd, max_depth(it));

    return maxd;
  }


  template <class T>
  int tree<T>::max_depth(const iterator_base& pos) const
  {
    NodePtr tmp=pos.node;

    if(tmp==0 || tmp==head || tmp==feet) return -1;

    int curdepth=0, maxdepth=0;
    while(true) { // try to walk the bottom of the tree
      while(tmp->m_first_child==0) {
        if(tmp==pos.node) return maxdepth;
        if(tmp->m_next_sib==0) {
          // try to walk up and then right again
          do {
            tmp=tmp->m_parent;
            if(tmp==0) return maxdepth;
            --curdepth;
          } while(tmp->m_next_sib==0);
        }
        if(tmp==pos.node) return maxdepth;
        tmp=tmp->m_next_sib;
      }
      tmp=tmp->m_first_child;
      ++curdepth;
      maxdepth=std::max(curdepth, maxdepth);
    } 
  }

  template <class T>
  unsigned int tree<T>::number_of_children(const iterator_base& it) 
  {
    NodePtr pos=it.node->m_first_child;
    if(pos==0) return 0;

    unsigned int ret=1;
    //        while(pos!=it.node->m_last_child) {
    //                ++ret;
    //                pos=pos->m_next_sib;
    //                }
    while((pos=pos->m_next_sib))
      ++ret;
    return ret;
  }

  template <class T>
  unsigned int tree<T>::number_of_siblings(const iterator_base& it) const
  {
    NodePtr pos=it.node;
    unsigned int ret=0;
    // count forward
    while(pos->m_next_sib && 
        pos->m_next_sib!=head &&
        pos->m_next_sib!=feet) {
      ++ret;
      pos=pos->m_next_sib;
    }
    // count backward
    pos=it.node;
    while(pos->m_prev_sib && 
        pos->m_prev_sib!=head &&
        pos->m_prev_sib!=feet) {
      ++ret;
      pos=pos->m_prev_sib;
    }

    return ret;
  }

  template <class T>
  bool tree<T>::is_valid(const iterator_base& it) const
  {
    if(it.node==0 || it.node==feet || it.node==head) return false;
    else return true;
  }

  template <class T>
  unsigned int tree<T>::index(sibling_iterator it) const
  {
    unsigned int ind=0;
    if(it.node->m_parent==0) {
      while(it.node->m_prev_sib!=head) {
        it.node=it.node->m_prev_sib;
        ++ind;
      }
    }
    else {
      while(it.node->m_prev_sib!=0) {
        it.node=it.node->m_prev_sib;
        ++ind;
      }
    }
    return ind;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::sibling(const iterator_base& it, unsigned int num)
  {
    NodePtr tmp;
    if(it.node->m_parent==0) {
      tmp=head->m_next_sib;
      while(num) {
        tmp = tmp->m_next_sib;
        --num;
      }
    }
    else {
      tmp=it.node->m_parent->m_first_child;
      while(num) {
        assert(tmp!=0);
        tmp = tmp->m_next_sib;
        --num;
      }
    }
    return tmp;
  }

  template <class T>
  void tree<T>::debug_verify_consistency() const
  {
    iterator it=begin();
    while(it!=end()) {
      if(it.node->m_parent!=0) {
        if(it.node->m_prev_sib==0) 
          assert(it.node->m_parent->m_first_child==it.node);
        else 
          assert(it.node->m_prev_sib->m_next_sib==it.node);
        if(it.node->m_next_sib==0) 
          assert(it.node->m_parent->m_last_child==it.node);
        else
          assert(it.node->m_next_sib->m_prev_sib==it.node);
      }
      ++it;
    }
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::child(const iterator_base& it, unsigned int num) 
  {
    NodePtr tmp=it.node->m_first_child;
    while(num--) {
      assert(tmp!=0);
      tmp=tmp->m_next_sib;
    }
    return tmp;
  }




  // Iterator base

  template <class T>
    tree<T>::iterator_base::iterator_base()
  : node(0), skip_current_children_(false)
  {
  }

  template <class T>
    tree<T>::iterator_base::iterator_base(NodePtr tn)
  : node(tn), skip_current_children_(false)
  {
  }

  template <class T>
  T& tree<T>::iterator_base::operator*() const
  {
    return node->m_value;
  }

  template <class T>
  T* tree<T>::iterator_base::operator->() const
  {
    return &(node->m_value);
  }

  template <class T>
  bool tree<T>::post_order_iterator::operator!=(const post_order_iterator& other) const
  {
    if(other.node!=this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::post_order_iterator::operator==(const post_order_iterator& other) const
  {
    if(other.node==this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::pre_order_iterator::operator!=(const pre_order_iterator& other) const
  {
    if(other.node!=this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::pre_order_iterator::operator==(const pre_order_iterator& other) const
  {
    if(other.node==this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::sibling_iterator::operator!=(const sibling_iterator& other) const
  {
    if(other.node!=this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::sibling_iterator::operator==(const sibling_iterator& other) const
  {
    if(other.node==this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::leaf_iterator::operator!=(const leaf_iterator& other) const
  {
    if(other.node!=this->node) return true;
    else return false;
  }

  template <class T>
  bool tree<T>::leaf_iterator::operator==(const leaf_iterator& other) const
  {
    if(other.node==this->node && other.top_node==this->top_node) return true;
    else return false;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::iterator_base::begin() const
  {
    if(node->m_first_child==0) 
      return end();

    sibling_iterator ret(node->m_first_child);
    ret.parent_=this->node;
    return ret;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::iterator_base::end() const
  {
    sibling_iterator ret(0);
    ret.parent_=node;
    return ret;
  }

  template <class T>
  void tree<T>::iterator_base::skip_children()
  {
    skip_current_children_=true;
  }

  template <class T>
  void tree<T>::iterator_base::skip_children(bool skip)
  {
    skip_current_children_=skip;
  }

  template <class T>
  unsigned int tree<T>::iterator_base::number_of_children() const
  {
    NodePtr pos=node->m_first_child;
    if(pos==0) return 0;

    unsigned int ret=1;
    while(pos!=node->m_last_child) {
      ++ret;
      pos=pos->m_next_sib;
    }
    return ret;
  }



  // Pre-order iterator

  template <class T>
    tree<T>::pre_order_iterator::pre_order_iterator() 
  : iterator_base(0)
  {
  }

  template <class T>
    tree<T>::pre_order_iterator::pre_order_iterator(NodePtr tn)
  : iterator_base(tn)
  {
  }

  template <class T>
    tree<T>::pre_order_iterator::pre_order_iterator(const iterator_base &other)
  : iterator_base(other.node)
  {
  }

  template <class T>
    tree<T>::pre_order_iterator::pre_order_iterator(const sibling_iterator& other)
  : iterator_base(other.node)
  {
    if(this->node==0) {
      if(other.range_last()!=0)
        this->node=other.range_last();
      else 
        this->node=other.parent_;
      this->skip_children();
      ++(*this);
    }
  }

  template <class T>
  typename tree<T>::pre_order_iterator& tree<T>::pre_order_iterator::operator++()
  {
    assert(this->node!=0);
    if(!this->skip_current_children_ && this->node->m_first_child != 0) {
      this->node=this->node->m_first_child;
    }
    else {
      this->skip_current_children_=false;
      while(this->node->m_next_sib==0) {
        this->node=this->node->m_parent;
        if(this->node==0)
          return *this;
      }
      this->node=this->node->m_next_sib;
    }
    return *this;
  }

  template <class T>
  typename tree<T>::pre_order_iterator& tree<T>::pre_order_iterator::operator--()
  {
    assert(this->node!=0);
    if(this->node->m_prev_sib) {
      this->node=this->node->m_prev_sib;
      while(this->node->m_last_child)
        this->node=this->node->m_last_child;
    }
    else {
      this->node=this->node->m_parent;
      if(this->node==0)
        return *this;
    }
    return *this;
  }

  template <class T>
  typename tree<T>::pre_order_iterator tree<T>::pre_order_iterator::operator++(int)
  {
    pre_order_iterator copy = *this;
    ++(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::pre_order_iterator& tree<T>::pre_order_iterator::next_skip_children() 
  {
    (*this).skip_children();
    (*this)++;
    return *this;
  }

  template <class T>
  typename tree<T>::pre_order_iterator tree<T>::pre_order_iterator::operator--(int)
  {
    pre_order_iterator copy = *this;
    --(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::pre_order_iterator& tree<T>::pre_order_iterator::operator+=(unsigned int num)
  {
    while(num>0) {
      ++(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  typename tree<T>::pre_order_iterator& tree<T>::pre_order_iterator::operator-=(unsigned int num)
  {
    while(num>0) {
      --(*this);
      --num;
    }
    return (*this);
  }



  // Post-order iterator

  template <class T>
    tree<T>::post_order_iterator::post_order_iterator() 
  : iterator_base(0)
  {
  }

  template <class T>
    tree<T>::post_order_iterator::post_order_iterator(NodePtr tn)
  : iterator_base(tn)
  {
  }

  template <class T>
    tree<T>::post_order_iterator::post_order_iterator(const iterator_base &other)
  : iterator_base(other.node)
  {
  }

  template <class T>
    tree<T>::post_order_iterator::post_order_iterator(const sibling_iterator& other)
  : iterator_base(other.node)
  {
    if(this->node==0) {
      if(other.range_last()!=0)
        this->node=other.range_last();
      else 
        this->node=other.parent_;
      this->skip_children();
      ++(*this);
    }
  }

  template <class T>
  typename tree<T>::post_order_iterator& tree<T>::post_order_iterator::operator++()
  {
    assert(this->node!=0);
    if(this->node->m_next_sib==0) {
      this->node=this->node->m_parent;
      this->skip_current_children_=false;
    }
    else {
      this->node=this->node->m_next_sib;
      if(this->skip_current_children_) {
        this->skip_current_children_=false;
      }
      else {
        while(this->node->m_first_child)
          this->node=this->node->m_first_child;
      }
    }
    return *this;
  }

  template <class T>
  typename tree<T>::post_order_iterator& tree<T>::post_order_iterator::operator--()
  {
    assert(this->node!=0);
    if(this->skip_current_children_ || this->node->m_last_child==0) {
      this->skip_current_children_=false;
      while(this->node->m_prev_sib==0)
        this->node=this->node->m_parent;
      this->node=this->node->m_prev_sib;
    }
    else {
      this->node=this->node->m_last_child;
    }
    return *this;
  }

  template <class T>
  typename tree<T>::post_order_iterator tree<T>::post_order_iterator::operator++(int)
  {
    post_order_iterator copy = *this;
    ++(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::post_order_iterator tree<T>::post_order_iterator::operator--(int)
  {
    post_order_iterator copy = *this;
    --(*this);
    return copy;
  }


  template <class T>
  typename tree<T>::post_order_iterator& tree<T>::post_order_iterator::operator+=(unsigned int num)
  {
    while(num>0) {
      ++(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  typename tree<T>::post_order_iterator& tree<T>::post_order_iterator::operator-=(unsigned int num)
  {
    while(num>0) {
      --(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  void tree<T>::post_order_iterator::descend_all()
  {
    assert(this->node!=0);
    while(this->node->m_first_child)
      this->node=this->node->m_first_child;
  }

  // Sibling iterator

  template <class T>
    tree<T>::sibling_iterator::sibling_iterator() 
  : iterator_base()
  {
    set_parent_();
  }

  template <class T>
    tree<T>::sibling_iterator::sibling_iterator(NodePtr tn)
  : iterator_base(tn)
  {
    set_parent_();
  }

  template <class T>
    tree<T>::sibling_iterator::sibling_iterator(const iterator_base& other)
  : iterator_base(other.node)
  {
    set_parent_();
  }

  template <class T>
    tree<T>::sibling_iterator::sibling_iterator(const sibling_iterator& other)
  : iterator_base(other), parent_(other.parent_)
  {
  }

  template <class T>
  void tree<T>::sibling_iterator::set_parent_()
  {
    parent_=0;
    if(this->node==0) return;
    if(this->node->m_parent!=0)
      parent_=this->node->m_parent;
  }

  template <class T>
  typename tree<T>::sibling_iterator& tree<T>::sibling_iterator::operator++()
  {
    if(this->node)
      this->node=this->node->m_next_sib;
    return *this;
  }

  template <class T>
  typename tree<T>::sibling_iterator& tree<T>::sibling_iterator::operator--()
  {
    if(this->node) this->node=this->node->m_prev_sib;
    else {
      assert(parent_);
      this->node=parent_->m_last_child;
    }
    return *this;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::sibling_iterator::operator++(int)
  {
    sibling_iterator copy = *this;
    ++(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::sibling_iterator tree<T>::sibling_iterator::operator--(int)
  {
    sibling_iterator copy = *this;
    --(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::sibling_iterator& tree<T>::sibling_iterator::operator+=(unsigned int num)
  {
    while(num>0) {
      ++(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  typename tree<T>::sibling_iterator& tree<T>::sibling_iterator::operator-=(unsigned int num)
  {
    while(num>0) {
      --(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  typename tree<T>::NodePtr tree<T>::sibling_iterator::range_first() const
  {
    NodePtr tmp=parent_->m_first_child;
    return tmp;
  }

  template <class T>
  typename tree<T>::NodePtr tree<T>::sibling_iterator::range_last() const
  {
    return parent_->m_last_child;
  }

  // Leaf iterator

  template <class T>
    tree<T>::leaf_iterator::leaf_iterator() 
  : iterator_base(0), top_node(0)
  {
  }

  template <class T>
    tree<T>::leaf_iterator::leaf_iterator(NodePtr tn, NodePtr top)
  : iterator_base(tn), top_node(top)
  {
  }

  template <class T>
    tree<T>::leaf_iterator::leaf_iterator(const iterator_base &other)
  : iterator_base(other.node), top_node(0)
  {
  }

  template <class T>
    tree<T>::leaf_iterator::leaf_iterator(const sibling_iterator& other)
  : iterator_base(other.node), top_node(0)
  {
    if(this->node==0) {
      if(other.range_last()!=0)
        this->node=other.range_last();
      else 
        this->node=other.parent_;
      ++(*this);
    }
  }

  template <class T>
  typename tree<T>::leaf_iterator& tree<T>::leaf_iterator::operator++()
  {
    assert(this->node!=0);
    if(this->node->m_first_child!=0) { // current node is no longer leaf (children got added)
      while(this->node->m_first_child) 
        this->node=this->node->m_first_child;
    }
    else {
      while(this->node->m_next_sib==0) { 
        if (this->node->m_parent==0) return *this;
        this->node=this->node->m_parent;
        if (top_node != 0 && this->node==top_node) return *this;
      }
      this->node=this->node->m_next_sib;
      while(this->node->m_first_child)
        this->node=this->node->m_first_child;
    }
    return *this;
  }

  template <class T>
  typename tree<T>::leaf_iterator& tree<T>::leaf_iterator::operator--()
  {
    assert(this->node!=0);
    while (this->node->m_prev_sib==0) {
      if (this->node->m_parent==0) return *this;
      this->node=this->node->m_parent;
      if (top_node !=0 && this->node==top_node) return *this; 
    }
    this->node=this->node->m_prev_sib;
    while(this->node->m_last_child)
      this->node=this->node->m_last_child;
    return *this;
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::leaf_iterator::operator++(int)
  {
    leaf_iterator copy = *this;
    ++(*this);
    return copy;
  }

  template <class T>
  typename tree<T>::leaf_iterator tree<T>::leaf_iterator::operator--(int)
  {
    leaf_iterator copy = *this;
    --(*this);
    return copy;
  }


  template <class T>
  typename tree<T>::leaf_iterator& tree<T>::leaf_iterator::operator+=(unsigned int num)
  {
    while(num>0) {
      ++(*this);
      --num;
    }
    return (*this);
  }

  template <class T>
  typename tree<T>::leaf_iterator& tree<T>::leaf_iterator::operator-=(unsigned int num)
  {
    while(num>0) {
      --(*this);
      --num;
    }
    return (*this);
  }

}; // end namespace polydsu_tree

#endif /* POLYDSU_TREE_TREE_H */
