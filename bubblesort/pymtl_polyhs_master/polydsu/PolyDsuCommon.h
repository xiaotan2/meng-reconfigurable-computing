//========================================================================
// PolyDsuCommon.h
//========================================================================
// Author  : Shreesha Srinath
// Date    : July 09, 2015

#ifndef POLYDUS_POLY_DSU_COMMON_H
#define POLYDUS_POLY_DSU_COMMON_H

#include <ap_int.h>

namespace polydsu {

  //----------------------------------------------------------------------
  // dtValue
  //----------------------------------------------------------------------

  struct dtValue {
    ap_uint<8> offset;
    ap_uint<8> size;
    ap_uint<8> type;
    ap_uint<8> fields;

    dtValue() : offset(0), size(0), type(0), fields(0) {}

    dtValue( ap_uint<32> value ) {
      offset = ( value >> 24 ) & 0xff;
      size   = ( value >> 16 ) & 0xff;
      type   = ( value >> 8  ) & 0xff;
      fields = ( value & 0xff );
    }

  };

}

#endif /* POLYDSU_POLY_DSU_COMMON_H */

