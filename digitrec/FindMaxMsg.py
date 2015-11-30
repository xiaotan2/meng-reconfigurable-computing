#=========================================================================
# FindMaxMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# FindMaxReqMsg
#-------------------------------------------------------------------------

class FindMaxReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField(6)

  def mk_msg( s, data ):
    msg       = s()
    msg.data  = data
    return msg

  def __str__( s ):
    return "{}".format( s.data )

#-------------------------------------------------------------------------
# FindMaxRespMsg
#-------------------------------------------------------------------------
class FindMaxRespMsg( BitStructDefinition ):
  
  def __init__( s ):
    s.data  = BitField(6)
    s.idx   = BitField(2)

  def mk_msg( s, data, idx ):
    msg       = s()
    msg.data  = data
    msg.idx   = idx
    return msg

  def __str__( s ):
    return "{}:{}".format( s.data, s.idx )
