#=========================================================================
# PolyDsuMsg
#=========================================================================
# Contains polydsu request and response messages.

from pymtl import *

#-------------------------------------------------------------------------
# PolyDsuReqMsg
#-------------------------------------------------------------------------
# The PolyDsuReqMsg bits are interpreted based on the opcode type
#
# Message Format:
#
#  106  96 95   88 87  85 84    0
#  +------+-------+------+-------+
#  | id   | opq   | opc  | msg   |
#  +------+-------+------+-------+
#
# PolyDsu Iterator Request Messages:
#
#  106  96 95   88 87  85 84   53 52   21 20    0
#  +------+-------+------+-------+-------+-------+
#  | id   | opq   | opc  | addr  | data  | iter  |
#  +------+-------+------+-------+-------+-------+
#
# MTX/MFX Request Messages:
#
#  106  96 95   88 87  85 84   80 79   48 47    0
#  +------+-------+------+-------+-------+-------+
#  | id   | opq   | opc  | raddr | rdata | 00000 |
#  +------+-------+------+-------+-------+-------+
#
#  opc:
#       0 = MFX
#       1 = MTX
#       2 = CFG
#       3 = GET
#       4 = SET
#       5 = INCR
#       6 = DECR

class PolyDsuReqMsg( BitStructDefinition ):

  # msg type
  TYPE_MFX  = 0
  TYPE_MTX  = 1
  TYPE_CFG  = 2
  TYPE_GET  = 3
  TYPE_SET  = 4
  TYPE_INCR = 5
  TYPE_DECR = 6

  # slices
  iter_ = slice( 0,21)
  data  = slice(21,53)
  addr  = slice(53,85)

  rdata = slice(48,80)
  raddr = slice(80,85)

  def __init__( s ):

    # field widths
    s.id_nbits  = 11
    s.opq_nbits =  8
    s.opc_nbits =  3
    s.msg_nbits = 85

    # primary fields
    s.id  = BitField( s.id_nbits  )
    s.opq = BitField( s.opq_nbits )
    s.opc = BitField( s.opc_nbits )
    s.msg = BitField( s.msg_nbits )

  # generic message
  def mk_msg( s, id_, opq, opc, msg ):

    bits     = s()
    bits.id  = id_
    bits.opq = opq
    bits.opc = opc
    bits.msg = msg

    return msg

  # mtx/mfx messages
  def mk_xcel_msg( s, id_, opq, opc, raddr, rdata ):

    bits            = s()
    bits.id         = id_
    bits.opq        = opq
    bits.opc        = opc

    bits[ PolyDsuReqMsg.raddr ] = raddr
    bits[ PolyDsuReqMsg.rdata ] = rdata

    return bits

  # dsu-iterator messages
  def mk_dsu_msg( s, id_, opq, opc, addr, data, iter_ ):

    bits            = s()
    bits.id         = id_
    bits.opq        = opq
    bits.opc        = opc

    bits[ PolyDsuReqMsg.addr  ] = addr
    bits[ PolyDsuReqMsg.data  ] = data
    bits[ PolyDsuReqMsg.iter_ ] = iter_

    return bits

  def __str__( s ):

    if   s.opc == PolyDsuReqMsg.TYPE_MFX:
      return "{}:{}:mfx:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_MTX:
      return "{}:{}:mtx:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_CFG:
      return "{}:{}:cfg:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_GET:
      return "{}:{}:get:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_SET:
      return "{}:{}:set:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_INCR:
      return "{}:{}:inc:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_DECR:
      return "{}:{}:dec:{}".format( s.id, s.opq, s.msg )

#-------------------------------------------------------------------------
# PolyDsuRespMsg
#-------------------------------------------------------------------------
# The PolyDsuRespMsg bits are interpreted based on the opcode type
#
# Message Format:
#
#  85   75 74   67 66  64 63    0
#  +------+-------+------+-------+
#  | id   | opq   | opc  | msg   |
#  +------+-------+------+-------+
#
# PolyDsu Iterator Response Messages:
#
#  85   75 74   67 66  64 63   32 31   0
#  +------+-------+------+-------+-------+
#  | id   | opq   | opc  | addr  | data  |
#  +------+-------+------+-------+-------+
#
# MTX/MFX Response Messages:
#
#  85   75 74   67 66  64 63   32 31    0
#  +------+-------+------+-------+-------+
#  | id   | opq   | opc  | rdata | 00000 |
#  +------+-------+------+-------+-------+
#
#  opc:
#       0 = MFX
#       1 = MTX
#       2 = CFG
#       3 = GET
#       4 = SET
#       5 = INCR
#       6 = DECR

class PolyDsuRespMsg( BitStructDefinition ):

  # msg type
  TYPE_MFX  = 0
  TYPE_MTX  = 1
  TYPE_CFG  = 2
  TYPE_GET  = 3
  TYPE_SET  = 4
  TYPE_INCR = 5
  TYPE_DECR = 6

  # slices
  data  = slice( 0,32)
  addr  = slice(32,64)

  rdata = slice(32,64)

  def __init__( s ):

    # field widths
    s.id_nbits  = 11
    s.opq_nbits =  8
    s.opc_nbits =  3
    s.msg_nbits = 64

    # primary fields
    s.id  = BitField( s.id_nbits  )
    s.opq = BitField( s.opq_nbits )
    s.opc = BitField( s.opc_nbits )
    s.msg = BitField( s.msg_nbits )

  # generic message
  def mk_msg( s, id_, opq, opc, msg ):

    bits     = s()
    bits.id  = id_
    bits.opq = opq
    bits.opc = opc
    bits.msg = msg

    return msg

  # mtx/mfx messages
  def mk_xcel_msg( s, id_, opq, opc, rdata ):

    bits            = s()
    bits.id         = id_
    bits.opq        = opq
    bits.opc        = opc

    bits[ PolyDsuRespMsg.rdata ] = rdata

    return bits

  # dsu-iterator messages
  def mk_dsu_msg( s, id_, opq, opc, addr, data ):

    bits            = s()
    bits.id         = id_
    bits.opq        = opq
    bits.opc        = opc

    bits[ PolyDsuRespMsg.addr  ] = addr
    bits[ PolyDsuRespMsg.data  ] = data

    return bits

  def __str__( s ):

    if   s.opc == PolyDsuRespMsg.TYPE_MFX:
      return "{}:{}:mfx:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuRespMsg.TYPE_MTX:
      return "{}:{}:mtx:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuReqMsg.TYPE_CFG:
      return "{}:{}:cfg:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuRespMsg.TYPE_GET:
      return "{}:{}:get:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuRespMsg.TYPE_SET:
      return "{}:{}:set:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuRespMsg.TYPE_INCR:
      return "{}:{}:inc:{}".format( s.id, s.opq, s.msg )
    elif s.opc == PolyDsuRespMsg.TYPE_DECR:
      return "{}:{}:dec:{}".format( s.id, s.opq, s.msg )

