#=========================================================================
# ReducerMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# ReducerReqMsg
#-------------------------------------------------------------------------

class ReducerReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField( 6 )
    s.digit = BitField( 4 )
    s.type_ = BitField( 1 )

  def mk_msg( s, data, digit, type_ ):
    msg       = s()
    msg.data  = data
    msg.digit = digit
    msg.type_ = type_
    return msg

  def __str__( s ):
    return "{}:{}:{}".format( s.data, s.digit, s.type_ )

class ReducerRespMsg( BitStructDefinition ):
  

  def __init__( s ):
    s.data  = BitField( 6 )
    s.digit = BitField( 4 )
    s.type_ = BitField( 1 )

  def mk_msg( s, data, digit, type_ ):
    msg       = s()
    msg.data  = data
    msg.digit = digit
    msg.type_ = type_
    return msg

  def __str__( s ):
    return "{}:{}:{}".format( s.data, s.digit, s.type_ )

