//========================================================================
// Graph inline functions
//========================================================================
// Authors : Shreesha Srinath, Ritchie Zhao
// Date    : September 17, 2014
// Project : Polymorphic Hardware Specialization
//
// aph container implementation inspired from Boost:graph

//----------------------------------------------------------------------
// Bellman-Ford
//----------------------------------------------------------------------
// computes single source shortest paths

template<typename T>
bool _Graph<T>::bellman_ford( vertex_iterator src ) {
  // upper bound on distance
  const int ubound = 1 << 30;

  // set all node labels to upper bound
  for (vertex_iterator v = begin_vertices(), ve = end_vertices();
       v != ve; ++v)
  {
    get_label(v) = ubound;
  }
  
  // set src label to 0
  get_label(src) = 0;
  
  // Bellman-Ford Algorithm
  for (unsigned i = 0; i < num_vertices()-1; ++i) {
    for (edge_iterator e = begin_edges(), ee = end_edges();
         e != ee; ++e) {
      
      int src_label = get_label(get_src(e));
      int weight = get_weight(e);
      vertex_iterator dst = get_dst(e);
      
      if (src_label + weight < get_label(dst)) {
        get_label(dst) = src_label + weight;
      }
    }
  }

  // Check for negative cycles
  for (edge_iterator e = begin_edges(), ee = end_edges();
       e != ee; ++e) {
    int src_label = get_label(get_src(e));
    int weight = get_weight(e);
    vertex_iterator dst = get_dst(e);
    if (src_label + weight < get_label(dst)) {
      return false;
    }
  }

  return true;
}
