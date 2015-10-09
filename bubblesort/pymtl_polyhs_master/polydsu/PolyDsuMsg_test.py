#=========================================================================
# PolyDsuMsg_test
#=========================================================================
# Test suite for the polydsu messages

from pymtl      import *
from PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg

#-------------------------------------------------------------------------
# test_xcelmfx_fields
#-------------------------------------------------------------------------

def test_xcelmfx_fields():

  # create mfx request msg
  #                                         id   opq                     opc  raddr  rdata
  mfx_req = PolyDsuReqMsg().mk_xcel_msg( 0x008, 0x53, PolyDsuReqMsg.TYPE_MFX,  0x14,     0 )

  # verify msg
  assert mfx_req.id  == 0x008
  assert mfx_req.opq == 0x53
  assert mfx_req.opc == PolyDsuReqMsg.TYPE_MFX

  assert mfx_req[ PolyDsuReqMsg.raddr ] == 0x14
  assert mfx_req[ PolyDsuReqMsg.rdata ] == 0

  # create mfx response msg
  #                                           id   opq                      opc       rdata
  mfx_resp = PolyDsuRespMsg().mk_xcel_msg( 0x008, 0x53, PolyDsuRespMsg.TYPE_MFX, 0xdeadbeef )

  # verify msg
  assert mfx_resp.id  == 0x008
  assert mfx_resp.opq == 0x53
  assert mfx_resp.opc == PolyDsuRespMsg.TYPE_MFX

  assert mfx_resp[ PolyDsuRespMsg.rdata ] == 0xdeadbeef

#-------------------------------------------------------------------------
# test_xcelmtx_fields
#-------------------------------------------------------------------------

def test_xcelmtx_fields():

  # create mtx request msg
  #                                         id   opq                     opc  raddr       rdata
  mtx_req = PolyDsuReqMsg().mk_xcel_msg( 0x008, 0x53, PolyDsuReqMsg.TYPE_MTX,  0x14, 0x8badf00d )

  # verify msg
  assert mtx_req.id  == 0x008
  assert mtx_req.opq == 0x53
  assert mtx_req.opc == PolyDsuReqMsg.TYPE_MTX

  assert mtx_req[ PolyDsuReqMsg.raddr ] == 0x14
  assert mtx_req[ PolyDsuReqMsg.rdata ] == 0x8badf00d

  # create mtx response msg
  #                                           id   opq                      opc  rdata
  mtx_resp = PolyDsuRespMsg().mk_xcel_msg( 0x008, 0x53, PolyDsuRespMsg.TYPE_MTX,     0 )

  # verify msg
  assert mtx_resp.id  == 0x008
  assert mtx_resp.opq == 0x53
  assert mtx_resp.opc == PolyDsuRespMsg.TYPE_MTX

  assert mtx_resp[ PolyDsuRespMsg.rdata ] == 0

#-------------------------------------------------------------------------
# test_dsuget_fields
#-------------------------------------------------------------------------

def test_dsuget_fields():

  # create dsu request msg
  #                                        id   opq                     opc        addr data   iter
  get_req = PolyDsuReqMsg().mk_dsu_msg( 0x401, 0xff, PolyDsuReqMsg.TYPE_GET, 0xaaaabbbb,   0, 0x123 )

  # verify msg
  assert get_req.id  == 0x401
  assert get_req.opq == 0xff
  assert get_req.opc == PolyDsuReqMsg.TYPE_GET

  assert get_req[ PolyDsuReqMsg.addr  ] == 0xaaaabbbb
  assert get_req[ PolyDsuReqMsg.data  ] == 0
  assert get_req[ PolyDsuReqMsg.iter_ ] == 0x123

  # create dsu response msg
  #                                          id               opq          opc  addr        data
  get_resp = PolyDsuRespMsg().mk_dsu_msg( get_req.id, get_req.opq, get_req.opc,    0, 0xdead100c )

  # verify msg
  assert get_resp.id  == 0x401
  assert get_resp.opq == 0xff
  assert get_resp.opc == PolyDsuRespMsg.TYPE_GET

  assert get_resp[ PolyDsuRespMsg.addr ] == 0
  assert get_resp[ PolyDsuRespMsg.data ] == 0xdead100c
