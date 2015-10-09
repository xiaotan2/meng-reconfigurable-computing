//========================================================================
// PolyHS graph header
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : September 17, 2014
// Project : Polymorphic Hardware Specialization
//
// Graph container implementation inspired from Boost:graph

#ifndef POLYHS_GRAPH_H
#define POLYHS_GRAPH_H

#include <cstddef>
#include <iostream>
#include "polydsu_list/List.h"
#include "polydsu_graph/GraphProxy.h"

//------------------------------------------------------------------------
// PolyHS graph container
//------------------------------------------------------------------------

template<typename T>
class _Graph {

  public:
    typedef size_t                          size_type;

    typedef xmem::MemPointer< _Vertex<T> >  VertexPtr;
    typedef xmem::MemPointer< _Edge<T> >    EdgePtr;
    typedef list<_Vertex, T>                VertexList;
    typedef list<_Edge, T>                  EdgeList;
    typedef typename VertexList::iterator   vertex_iterator;
    typedef typename EdgeList::iterator     edge_iterator;

  //----------------------------------------------------------------------
  // Structure to store all nodes in the graph
  //----------------------------------------------------------------------
  private:
    VertexList  m_vertices;
    EdgeList    m_edges;
    
  public:
    //--------------------------------------------------------------------
    // Constructors
    //--------------------------------------------------------------------
    _Graph(
        xmem::Address vertices_ptr,
        xmem::Address edges_ptr,
        xmem::Opaque opq,
        xmem::MemReqStream& memreq,
        xmem::MemRespStream& memresp
    )
      : m_vertices( vertices_ptr, opq, memreq, memresp ),
        m_edges( edges_ptr, opq, memreq, memresp )
    {}
    
    //--------------------------------------------------------------------
    // Add vertex/edge
    //--------------------------------------------------------------------

    vertex_iterator add_vertex( VertexPtr v ) {
      return m_vertices.push_back(v);
    }
    vertex_iterator begin_vertices() {
      return m_vertices.begin();
    }
    vertex_iterator end_vertices() {
      return m_vertices.end();
    }

    edge_iterator add_edge( EdgePtr e ) {
      return m_edges.push_back(e);
    }
    edge_iterator begin_edges() {
      return m_edges.begin();
    }
    edge_iterator end_edges() {
      return m_edges.end();
    }

    
    //--------------------------------------------------------------------
    // Accessors
    //--------------------------------------------------------------------
    xmem::MemValue<T>& get_data(vertex_iterator vi) {
      return vi.get_ptr()->m_data;
    }
    const xmem::MemValue<T>& get_data(const vertex_iterator vi) const {
      return vi.get_ptr()->m_data;
    }
    
    xmem::MemValue<int>& get_label(vertex_iterator vi) {
      return vi.get_ptr()->m_label;
    }
    const xmem::MemValue<int>& get_label(const vertex_iterator vi) const {
      return vi.get_ptr()->m_label;
    }

    xmem::MemValue<int>& get_weight(edge_iterator ei) {
      return ei.get_ptr()->m_weight;
    }
    const xmem::MemValue<int>& get_weight(const edge_iterator ei) const {
      return ei.get_ptr()->m_weight;
    }
    
    vertex_iterator get_src(edge_iterator ei) {
      VertexPtr p = ei.get_ptr()->src;
      return (VertexPtr)(ei.get_ptr()->src);
    }
    const vertex_iterator get_src(const edge_iterator ei) const {
      return (VertexPtr)(ei.get_ptr()->src);
    }
    vertex_iterator get_dst(edge_iterator ei) {
      return (VertexPtr)(ei.get_ptr()->dst);
    }
    const vertex_iterator get_dst(const edge_iterator ei) const {
      return (VertexPtr)(ei.get_ptr()->dst);
    }

    size_t num_vertices () const { return m_vertices.size(); }
    size_t num_edges () const { return m_edges.size(); }

    //--------------------------------------------------------------------
    // Algorithms
    //--------------------------------------------------------------------

    // SSSP: Bellman-Ford
    bool bellman_ford( vertex_iterator src );
    
};

#include "Graph.inl"
#endif /* POLYHS_GRAPH_H */
