#=========================================================================
# CommitMsg
#=========================================================================

from pymtl      import *

#-------------------------------------------------------------------------
# CommitReqMsg
#-------------------------------------------------------------------------

class CommitReqMsg( BitStructDefinition ):

  def __init__( s, seq_num_nbits=8 ):

    s.opaque  = BitField( seq_num_nbits )
    s.xcel_id = BitField( 11 )
    s.valid   = BitField(  1 )
    s.seq_num = BitField( seq_num_nbits )

  def mk_msg( s, opaque, xcel_id, val, num ):
    msg         = s()
    msg.opaque  = opaque
    msg.xcel_id = xcel_id
    msg.valid   = val
    msg.seq_num = num
    return msg

  def __str__( s ):
    if s.valid:
      return "{}:{}:c:{}".format(
        s.opaque,
        s.xcel_id,
        s.seq_num
      )
    else:
      return "{}:{}:s:{}".format(
        s.opaque,
        s.xcel_id,
        s.seq_num
      )

#-------------------------------------------------------------------------
# CommitRespMsg
#-------------------------------------------------------------------------

class CommitRespMsg( BitStructDefinition ):

  def __init__( s, seq_num_nbits=8 ):

    s.opaque  = BitField( seq_num_nbits )
    s.xcel_id = BitField( 11 )
    s.seq_num = BitField( seq_num_nbits )

  def mk_msg( s, opaque, xcel_id, num ):
    msg         = s()
    msg.opaque  = opaque
    msg.xcel_id = xcel_id
    msg.seq_num = num
    return msg

  def __str__( s ):
    return "{}:{}:{}".format(
      s.opaque,
      s.xcel_id,
      s.seq_num
    )
