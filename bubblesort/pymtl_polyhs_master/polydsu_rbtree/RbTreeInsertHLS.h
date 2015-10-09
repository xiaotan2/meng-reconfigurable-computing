//========================================================================
// RbTreeInsertHLS.h
//========================================================================

#ifndef POLYDSU_RBTREE_RB_TREE_INSERT_HLS_H
#define POLYDSU_RBTREE_RB_TREE_INSERT_HLS_H

#include "xmem/MemMsg.h"
#include "xcel/XcelMsg.h"
#include "polydsu_rbtree/RbTree.h"

typedef int                 Key;
typedef int                 Value;
typedef RbTree<Key, Value>  Tree;
typedef Tree::NodePtr     NodePtr;
typedef Tree::iterator    iterator;

//--------------------------------------------------------------------
// HLS Insert Function
//--------------------------------------------------------------------
iterator m_insert_hls(
    NodePtr m_header, // header node for a tree
    NodePtr x,
    NodePtr y,
    NodePtr z,        // node to insert, unitialized
    const Key& k
);

iterator insert_unique_hls(
    NodePtr m_header,
    NodePtr mem,
    const Key& _k
);

//--------------------------------------------------------------------
// HLS Top Function
//--------------------------------------------------------------------
void RbTreeInsertHLS(
  hls::stream<xcel::XcelReqMsg>&  xcelreq,
  hls::stream<xcel::XcelRespMsg>& xcelresp,
  xmem::MemReqStream&             memreq,
  xmem::MemRespStream&            memresp
);

#endif /* POLYDSU_RBTREE_RB_TREE_INSERT_HLS_H */

