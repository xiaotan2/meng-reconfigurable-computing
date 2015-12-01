#=========================================================================
# FindMinMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# FindMinReqMsg
#-------------------------------------------------------------------------

class FindMinReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField(8)

  def mk_msg( s, data ):
    msg       = s()
    msg.data  = data
    return msg

  def __str__( s ):
    return "{}".format( s.data )

#-------------------------------------------------------------------------
# FindMinRespMsg
#-------------------------------------------------------------------------
class FindMinRespMsg( BitStructDefinition ):
  
  def __init__( s ):
    s.data    = BitField(8)
    s.digit   = BitField(4)

  def mk_msg( s, data, digit ):
    msg       = s()
    msg.data  = data
    msg.digit = digit
    return msg

  def __str__( s ):
    return "{}:{}".format( s.data, s.digit )
