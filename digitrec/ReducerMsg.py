#=========================================================================
# ReducerMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# ReducerReqMsg
#-------------------------------------------------------------------------

class ReducerReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField(49)
    s.digit = BitField( 4)

  def mk_msg( s, data, digit ):
    msg       = s()
    msg.data  = data
    msg.digit = digit
    return msg

  def __str__( s ):
    return "{}:{}".format( s.data, s.digit )

class ReducerRespMsg( BitStructDefinition ):
  

  def __init__( s ):
    s.data  = BitField(49)
    s.digit = BitField( 4)

  def mk_msg( s, data, digit ):
    msg       = s()
    msg.data  = data
    msg.digit = digit
    return msg

  def __str__( s ):
    return "{}:{}".format( s.data, s.digit )

