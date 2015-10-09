//========================================================================
// Unit Tests for MemMsg
//========================================================================

#include "utst/utst.h"
#include "polydsu/PolyDsuMsg.h"

using namespace polydsu;

//------------------------------------------------------------------------
// Test Mfx Messages
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMfx )
{

  //                    id   opq                      opc  raddr  rdata
  PolyDsuReqMsg req( 0x008, 0x53, PolyDsuReqMsg::TYPE_MFX,  0x14,     0 );

  UTST_CHECK_EQ( req.id(),     0x008 );
  UTST_CHECK_EQ( req.opq(),     0x53 );
  UTST_CHECK_EQ( req.opc(),        0 );
  UTST_CHECK_EQ( req.raddr(),   0x14 );
  UTST_CHECK_EQ( req.rdata(),      0 );

  //                         id        opq                       opc       rdata
  PolyDsuRespMsg resp( req.id(), req.opq(), PolyDsuRespMsg::TYPE_MFX, 0xdeadbeef );

  UTST_CHECK_EQ( resp.id(),         0x008 );
  UTST_CHECK_EQ( resp.opq(),         0x53 );
  UTST_CHECK_EQ( resp.opc(),            0 );
  UTST_CHECK_EQ( resp.rdata(), 0xdeadbeef );

};

//------------------------------------------------------------------------
// Test Mtx Messages
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestMtx )
{

  //                    id   opq                      opc  raddr       rdata
  PolyDsuReqMsg req( 0x008, 0x53, PolyDsuReqMsg::TYPE_MTX,  0x14, 0xdeadaabb );

  UTST_CHECK_EQ( req.id(),         0x008 );
  UTST_CHECK_EQ( req.opq(),         0x53 );
  UTST_CHECK_EQ( req.opc(),            1 );
  UTST_CHECK_EQ( req.raddr(),       0x14 );
  UTST_CHECK_EQ( req.rdata(), 0xdeadaabb );

  //                         id        opq       opc  rdata
  PolyDsuRespMsg resp( req.id(), req.opq(), req.opc(),    0 );

  UTST_CHECK_EQ( resp.id(),    0x008 );
  UTST_CHECK_EQ( resp.opq(),    0x53 );
  UTST_CHECK_EQ( resp.opc(),       1 );
  UTST_CHECK_EQ( resp.rdata(),     0 );

};

//------------------------------------------------------------------------
// Test Get Messages
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestGet )
{
  static const int ref_opc = PolyDsuReqMsg::TYPE_GET;

  //                    id   opq                      opc        addr data iter
  PolyDsuReqMsg req( 0x403, 0xff, PolyDsuReqMsg::TYPE_GET, 0xaabbccdd,   0,   0 );

  UTST_CHECK_EQ( req.id(),        0x403 );
  UTST_CHECK_EQ( req.opq(),        0xff );
  UTST_CHECK_EQ( req.opc(),     ref_opc );
  UTST_CHECK_EQ( req.addr(), 0xaabbccdd );
  UTST_CHECK_EQ( req.data(),          0 );
  UTST_CHECK_EQ( req.iter(),          0 );

  //                      id   opq                       opc addr        data
  PolyDsuRespMsg resp( 0x007, 0xf8, PolyDsuRespMsg::TYPE_GET,   0, 0xdeadbeef );

  UTST_CHECK_EQ( resp.id(),        0x007 );
  UTST_CHECK_EQ( resp.opq(),        0xf8 );
  UTST_CHECK_EQ( resp.opc(),     ref_opc );
  UTST_CHECK_EQ( resp.addr(),          0 );
  UTST_CHECK_EQ( resp.data(), 0xdeadbeef );

};

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv, "polydsu" );
}

