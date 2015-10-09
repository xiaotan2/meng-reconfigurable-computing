//========================================================================
// PolyDsuRbTreeHLS.h
//========================================================================
// Author  : Ritchie Zhao
// Date    : Aug 24, 2015
//
// C++ implementation of the rbtree data-structure unit. The rbtree
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#include <ap_utils.h>
#include <hls_stream.h>

#include "xmem/MemMsg.h"
#include "polydsu/PolyDsuCommon.h"
#include "polydsu/PolyDsuMsg.h"

#include "polydsu_rbtree/RbTree.h"
#include "polydsu_rbtree/RbTreeProxy.h"

typedef RbTree<int,int> rbtree;
typedef rbtree::Node    rbtree_node;
typedef rbtree::NodePtr rbtree_node_ptr;

//------------------------------------------------------------------------
// PolyDsuRbTreeHLS
//------------------------------------------------------------------------

void PolyDsuRbTreeHLS(
  hls::stream<polydsu::PolyDsuReqMsg>&   xcelreq,
  hls::stream<polydsu::PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&                    memreq,
  xmem::MemRespStream&                   memresp
);
