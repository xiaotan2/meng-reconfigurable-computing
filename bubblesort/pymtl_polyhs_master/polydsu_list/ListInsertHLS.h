//========================================================================
// ListInsertHLS.h
//========================================================================

#ifndef POLYDSU_LIST_LIST_INSERT_HLS_H
#define POLYDSU_LIST_LIST_INSERT_HLS_H

#include <ap_utils.h>
#include <assert.h>

#include "xmem/MemMsg.h"
#include "xmem/MemCommon.h"

#include "xcel/XcelMsg.h"

#include "polydsu_list/List.h"

typedef int                   Type;
typedef list<_ListNode,Type>  List;

void ListInsertHLS(
  hls::stream<xcel::XcelReqMsg>&   xcelreq,
  hls::stream<xcel::XcelRespMsg>&  xcelresp,
  xmem::MemReqStream&              memreq,
  xmem::MemRespStream&             memresp
);

#endif /* POLYDSU_LIST_LIST_INSERT_HLS_H */

