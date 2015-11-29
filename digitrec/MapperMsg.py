#=============================================================================
# MapperMsg
#=============================================================================

from pymtl import *

class MapperReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField( 49 )
    s.type_ = BitField( 1  )
    s.digit = BitField( 4  )

  def mk_msg( s, data, type, digit ):
    msg       = s()
    msg.data  = data
    msg.type_ = type
    msg.digit = digit
    return msg

  def __str__( s ):
    return "{}:{}:{}".format( s.data, s.type_, s.digit )

class MapperRespMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField( 49 )
    s.type_ = BitField( 1  )
    s.digit = BitField( 4  )

  def mk_msg( s, data, type, digit ):
    msg       = s()
    msg.data  = data
    msg.type_ = type
    msg.digit = digit
    return msg

  def __str__( s ):
    return "{}:{}:{}".format( s.data, s.type_, s.digit )
