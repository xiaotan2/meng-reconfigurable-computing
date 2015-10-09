//========================================================================
// PolyDsuBinTreeHLS.h
//========================================================================
// Author  : Ritchie Zhao
// Date    : Aug 24, 2015
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#include <ap_utils.h>
#include <hls_stream.h>

#include "xmem/MemMsg.h"
#include "polydsu/PolyDsuCommon.h"
#include "polydsu/PolyDsuMsg.h"

#include "polydsu_bintree/BinTree.h"
#include "polydsu_bintree/BinTreeProxy.h"

typedef BinTree<int> bintree;
typedef bintree::Node    bintree_node;
typedef bintree::NodePtr bintree_node_ptr;

//------------------------------------------------------------------------
// PolyDsuBinTreeHLS
//------------------------------------------------------------------------

void PolyDsuBinTreeHLS(
  hls::stream<polydsu::PolyDsuReqMsg>&   xcelreq,
  hls::stream<polydsu::PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&                    memreq,
  xmem::MemRespStream&                   memresp
);
