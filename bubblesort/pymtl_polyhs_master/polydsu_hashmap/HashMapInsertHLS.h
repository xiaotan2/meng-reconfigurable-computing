//========================================================================
// HashMapInsertHLS.h
//========================================================================

#ifndef POLYDSU_HASH_MAP_HASH_MAP_INSERT_H
#define POLYDSU_HASH_MAP_HASH_MAP_INSERT_H

#include "xmem/MemMsg.h"
#include "xmem/MemCommon.h"
#include "xmem/ArrayMemPortAdapter.h"

#include "polydsu/PolyDsuMsg.h"

#include "polydsu_hashmap/HashMapEntryProxy.h"

//------------------------------------------------------------------------
// HashMapInsertHLS
//------------------------------------------------------------------------

void HashMapInsertHLS(
  hls::stream<polydsu::PolyDsuReqMsg>&   xcelreq,
  hls::stream<polydsu::PolyDsuRespMsg>&  xcelresp,
  xmem::MemReqStream&                    memreq,
  xmem::MemRespStream&                   memresp
);


#endif /* POLYDSU_HASH_MAP_HASH_MAP_INSERT_H */
