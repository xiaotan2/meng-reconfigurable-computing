//========================================================================
// RbTreeInsertHLS.cc
//========================================================================

#include <ap_utils.h>
#include <assert.h>

#include "polydsu_rbtree/RbTreeInsertHLS.h"

//-------------------------------------------------------------------
// Tree::insert
// Note that the real insert function would allocate node z using
//  z = m_create_node(key,val)
// It would also increment m_node_count in the tree
//-------------------------------------------------------------------
iterator m_insert_hls(
    NodePtr m_header, // header node for a tree
    NodePtr x,
    NodePtr y,
    NodePtr z,        // node to insert, unitialized
    const Key& k
) {
  if (y == m_header || x != 0 ||
      (k < Tree::s_key(y))) {
    z->m_key = k;
    Tree::s_left(y) = z;               // also makes m_header->m_left = z
                                      //    when y == m_header
    if (y == m_header) {
      m_header->m_parent = z;
      m_header->m_right = z;
    }
    else if (y == m_header->m_left)
      m_header->m_left = z;   // maintain m_header->m_left pointing to min node
  }
  else {
    z->m_key = k;
    Tree::s_right(y) = z;
    if (y == m_header->m_right)
      m_header->m_right = z;  // maintain m_header->m_right pointing to max node
  }
  Tree::s_parent(z) = y;
  Tree::s_left(z) = 0;
  Tree::s_right(z) = 0;
  _RbTreeRebalance(z, m_header->m_parent);
  //++m_node_count;
  return iterator(z);
}

iterator insert_unique_hls(
    NodePtr m_header,
    NodePtr mem,
    const Key& _k
){
  NodePtr y = m_header;
  NodePtr x = m_header->m_parent;
  bool comp = true;
  while (x != 0) {
    y = x;
    comp = (_k < Tree::s_key(x));
    x = comp ? Tree::s_left(x) : Tree::s_right(x);
  }
  bool empty_tree = false;
  iterator j = iterator(y);
  if (comp) {
    if (j == (iterator)(NodePtr)m_header->m_left)
      empty_tree = true;
    else
      --j;
  }
  if ( !empty_tree && !(Tree::s_key(j.m_node) < _k) )
    return j;
  return m_insert_hls(m_header, x, y, mem, _k);
}

//-------------------------------------------------------------------
// HLS top function
// We write this in a way such that any of the arch. registers
// can be configured in any order
// Address Map:
//   1 - base pointer of tree's m_header
//   2 - base pointer of the node to insert
//   2 - base pointer of the key to insert
//-------------------------------------------------------------------
void RbTreeInsertHLS(
  hls::stream<xcel::XcelReqMsg>&  xcelreq,
  hls::stream<xcel::XcelRespMsg>& xcelresp,
  xmem::MemReqStream&             memreq,
  xmem::MemRespStream&            memresp
){
  // architectural registers
  typedef ap_uint<32> DataType;
  static DataType s_header;
  static DataType s_node;
  static DataType s_key;
  static DataType s_result;

  xcel::XcelReqMsg req = xcelreq.read();
  ap_uint<32> addr = req.addr();

  if (req.type() == xcel::XcelReqMsg::TYPE_WRITE) {
    switch (addr) {
      case 0:
        /*printf ("starting work!\n");
        printf ("  header: %u!\n", s_header.to_uint());
        printf ("  node  : %u!\n", s_node.to_uint());
        printf ("  key   : %u!\n", s_key.to_uint());*/

        s_result = insert_unique_hls(
            NodePtr( s_header, req.opq(), memreq, memresp ),
            NodePtr( s_node, req.opq(), memreq, memresp ),
            (Key)s_key
        ).m_node.get_addr();

        break;
      case 1:
        s_header = req.data();        break;
      case 2:
        s_node = req.data();          break;
      case 3:
        s_key  = req.data();          break;
      default:
        break;
    }

    xcelresp.write( xcel::XcelRespMsg( req.opq(), req.type(), 0, req.id() ) );
  }
  else {
    DataType data = 0;

    switch (req.addr()) {
      case 0:
        data = s_result;        break;
      case 1:
        data = s_header;        break;
      case 2:
        data = s_node;          break;
      case 3:
        data = s_key;           break;
      default:
        break;
    }

    xcelresp.write( xcel::XcelRespMsg( req.opq(), req.type(), data, req.id() ) );
  }
}

