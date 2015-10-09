//========================================================================
// PolyDsuMsg.h
//========================================================================
// Header file that defines the structs used for the accelerator interfaces.

#include <ap_int.h>

#ifndef POLYDSU_POLY_DSU_MSG_H
#define POLYDSU_POLY_DSU_MSG_H

namespace polydsu {

  //----------------------------------------------------------------------
  // PolyDsuReqMsg
  //----------------------------------------------------------------------

  struct PolyDsuReqMsg {

    // field widths
    static const unsigned id_nbits    = 11;
    static const unsigned opq_nbits   =  8;
    static const unsigned opc_nbits   =  3;
    static const unsigned addr_nbits  = 32;
    static const unsigned data_nbits  = 32;
    static const unsigned iter_nbits  = 21;

    static const unsigned raddr_nbits =  5;
    static const unsigned rdata_nbits = 32;

    // field msb's lsb's
    static const unsigned iter_lsb  = 0;
    static const unsigned iter_msb  = iter_nbits - 1;

    static const unsigned data_lsb  = iter_msb + 1;
    static const unsigned data_msb  = iter_msb + data_nbits;

    static const unsigned addr_lsb  = data_msb + 1;
    static const unsigned addr_msb  = data_msb + addr_nbits;

    static const unsigned opc_lsb   = addr_msb + 1;
    static const unsigned opc_msb   = addr_msb + opc_nbits;

    static const unsigned opq_lsb   = opc_msb + 1;
    static const unsigned opq_msb   = opc_msb + opq_nbits;

    static const unsigned id_lsb    = opq_msb + 1;
    static const unsigned id_msb    = opq_msb + id_nbits;

    static const unsigned rdata_lsb = 48;
    static const unsigned rdata_msb = rdata_lsb + rdata_nbits - 1 ;

    static const unsigned raddr_lsb = rdata_msb + 1;
    static const unsigned raddr_msb = rdata_msb + raddr_nbits;

    static const unsigned msg_nbits = id_msb + 1;

    // typedef declarations
    typedef ap_range_ref<msg_nbits,false> BitSliceProxy;
    typedef ap_uint<msg_nbits>            Bits;

    //--------------------------------------------------------------------
    // message type
    //--------------------------------------------------------------------

    enum {
      TYPE_MFX,
      TYPE_MTX,
      TYPE_CFG,
      TYPE_GET,
      TYPE_SET,
      TYPE_INCR,
      TYPE_DECR
    };

    //--------------------------------------------------------------------
    // message bits
    //--------------------------------------------------------------------

    Bits bits;

    //--------------------------------------------------------------------
    // field mutators
    //--------------------------------------------------------------------

    BitSliceProxy id()    { return bits(    id_msb,    id_lsb ); }
    BitSliceProxy opq()   { return bits(   opq_msb,   opq_lsb ); }
    BitSliceProxy opc()   { return bits(   opc_msb,   opc_lsb ); }
    BitSliceProxy addr()  { return bits(  addr_msb,  addr_lsb ); }
    BitSliceProxy data()  { return bits(  data_msb,  data_lsb ); }
    BitSliceProxy iter()  { return bits(  iter_msb,  iter_lsb ); }
    BitSliceProxy raddr() { return bits( raddr_msb, raddr_lsb ); }
    BitSliceProxy rdata() { return bits( rdata_msb, rdata_lsb ); }

    //--------------------------------------------------------------------
    // field inspectors
    //--------------------------------------------------------------------

    BitSliceProxy id()    const { return bits(    id_msb,    id_lsb ); }
    BitSliceProxy opq()   const { return bits(   opq_msb,   opq_lsb ); }
    BitSliceProxy opc()   const { return bits(   opc_msb,   opc_lsb ); }
    BitSliceProxy addr()  const { return bits(  addr_msb,  addr_lsb ); }
    BitSliceProxy data()  const { return bits(  data_msb,  data_lsb ); }
    BitSliceProxy iter()  const { return bits(  iter_msb,  iter_lsb ); }
    BitSliceProxy raddr() const { return bits( raddr_msb, raddr_lsb ); }
    BitSliceProxy rdata() const { return bits( rdata_msb, rdata_lsb ); }

    //--------------------------------------------------------------------
    // constructors
    //--------------------------------------------------------------------

    PolyDsuReqMsg() : bits( 0 ) { }

    PolyDsuReqMsg( ap_uint<id_nbits>   id_,   ap_uint<opq_nbits>  opq_,
                   ap_uint<opc_nbits>  opc_,  ap_uint<addr_nbits> addr_,
                   ap_uint<data_nbits> data_, ap_uint<iter_nbits> iter_ )
      : bits( ( id_, opq_, opc_, addr_, data_, iter_ ) )
    { }

    PolyDsuReqMsg( ap_uint<id_nbits>    id_,   ap_uint<opq_nbits>   opq_,
                   ap_uint<opc_nbits>   opc_,  ap_uint<raddr_nbits> raddr_,
                   ap_uint<rdata_nbits> rdata_ )
      : bits( ( id_, opq_, opc_, raddr_, rdata_, ap_uint<48>(0) ) )
    { }

  };

  //----------------------------------------------------------------------
  // PolyDsuRespMsg
  //----------------------------------------------------------------------

  struct PolyDsuRespMsg {

    // field widths
    static const unsigned id_nbits    = 11;
    static const unsigned opq_nbits   =  8;
    static const unsigned opc_nbits   =  3;
    static const unsigned addr_nbits  = 32;
    static const unsigned data_nbits  = 32;

    static const unsigned raddr_nbits =  5;
    static const unsigned rdata_nbits = 32;

    // field msb's lsb's
    static const unsigned data_lsb  = 0;
    static const unsigned data_msb  = data_nbits - 1;

    static const unsigned addr_lsb  = data_msb + 1;
    static const unsigned addr_msb  = data_msb + addr_nbits;

    static const unsigned opc_lsb   = addr_msb + 1;
    static const unsigned opc_msb   = addr_msb + opc_nbits;

    static const unsigned opq_lsb   = opc_msb + 1;
    static const unsigned opq_msb   = opc_msb + opq_nbits;

    static const unsigned id_lsb    = opq_msb + 1;
    static const unsigned id_msb    = opq_msb + id_nbits;

    static const unsigned rdata_lsb = 32;
    static const unsigned rdata_msb = rdata_lsb + rdata_nbits - 1 ;

    static const unsigned msg_nbits = id_msb + 1;

    // typedef declarations
    typedef ap_range_ref<msg_nbits,false> BitSliceProxy;
    typedef ap_uint<msg_nbits>            Bits;

    //--------------------------------------------------------------------
    // message type
    //--------------------------------------------------------------------

    enum {
      TYPE_MFX,
      TYPE_MTX,
      TYPE_CFG,
      TYPE_GET,
      TYPE_SET,
      TYPE_INCR,
      TYPE_DECR
    };

    //--------------------------------------------------------------------
    // message bits
    //--------------------------------------------------------------------

    Bits bits;

    //--------------------------------------------------------------------
    // field mutators
    //--------------------------------------------------------------------

    BitSliceProxy id()    { return bits(    id_msb,    id_lsb ); }
    BitSliceProxy opq()   { return bits(   opq_msb,   opq_lsb ); }
    BitSliceProxy opc()   { return bits(   opc_msb,   opc_lsb ); }
    BitSliceProxy addr()  { return bits(  addr_msb,  addr_lsb ); }
    BitSliceProxy data()  { return bits(  data_msb,  data_lsb ); }
    BitSliceProxy rdata() { return bits( rdata_msb, rdata_lsb ); }

    //--------------------------------------------------------------------
    // field inspectors
    //--------------------------------------------------------------------

    BitSliceProxy id()    const { return bits(    id_msb,    id_lsb ); }
    BitSliceProxy opq()   const { return bits(   opq_msb,   opq_lsb ); }
    BitSliceProxy opc()   const { return bits(   opc_msb,   opc_lsb ); }
    BitSliceProxy addr()  const { return bits(  addr_msb,  addr_lsb ); }
    BitSliceProxy data()  const { return bits(  data_msb,  data_lsb ); }
    BitSliceProxy rdata() const { return bits( rdata_msb, rdata_lsb ); }

    //--------------------------------------------------------------------
    // constructors
    //--------------------------------------------------------------------

    PolyDsuRespMsg() : bits( 0 ) { }

    PolyDsuRespMsg( ap_uint<id_nbits>   id_,  ap_uint<opq_nbits>  opq_,
                    ap_uint<opc_nbits>  opc_, ap_uint<addr_nbits> addr_,
                    ap_uint<data_nbits> data_ )
      : bits( ( id_, opq_, opc_, addr_, data_ ) )
    { }

    PolyDsuRespMsg( ap_uint<id_nbits>    id_,  ap_uint<opq_nbits>   opq_,
                    ap_uint<opc_nbits>   opc_, ap_uint<rdata_nbits> rdata_ )
      : bits( ( id_, opq_, opc_, rdata_, ap_uint<32>(0) ) )
    { }

  };

}

#endif /* POLYDSU_POLY_DSU_MSG_H */

