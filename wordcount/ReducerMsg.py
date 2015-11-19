#=========================================================================
# ReducerMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# ReducerReqMsg
#-------------------------------------------------------------------------

class ReducerReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.data  = BitField(1)
    s.type_ = BitField(1)

  def mk_msg( s, data, type ):
    msg       = s()
    msg.data  = data
    msg.type_ = type
    return msg

  def __str__( s ):
    return "{}:{}".format( s.data, s.type_ )

