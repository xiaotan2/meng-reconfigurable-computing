//========================================================================
// PolyDsuListHLS.h
//========================================================================
// Author  : Shreesha Srinath
// Date    : July 09, 2015
//
// C++ implementation of the list data-structure unit. The list
// data-structure unit has a data-structure request interface over which it
// receives a message sent by the dispatch unit to service a iterator-based
// request. The results of the computation are returned to the processor
// via the iterator response interface.
//
// NOTE: Currently the design handles only primitive data-types.
// TBD: Handle user-defined data-types.

#ifndef POLYDSU_LIST_POLY_DSU_LIST_HLS_H
#define POLYDSU_LIST_POLY_DSU_LIST_HLS_H

#include <ap_utils.h>
#include <hls_stream.h>

#include "xmem/MemMsg.h"
#include "polydsu/PolyDsuCommon.h"
#include "polydsu/PolyDsuMsg.h"

#include "polydsu_list/List.h"
#include "polydsu_list/ListProxy.h"

typedef xmem::MemValue<_ListNode<int> >   list_node;
typedef xmem::MemPointer<_ListNode<int> > list_node_ptr;

typedef list<_ListNode,int> List;

//------------------------------------------------------------------------
// PolyDsuListHLS
//------------------------------------------------------------------------

void PolyDsuListHLS(
  hls::stream<polydsu::PolyDsuReqMsg>&   xcelreq,
  hls::stream<polydsu::PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&                    memreq,
  xmem::MemRespStream&                   memresp
);

#endif /* POLYDSU_LIST_POLY_DSU_LIST_HLS_H */

