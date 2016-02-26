
from pymtl import *

class pageRankReqMsg( BitStructDefinition ):


  TYPE_READ = 0
  TYPE_WRITE = 1
  def __init__( s ):
    s.data  = BitField ( 32 )
    s.addr  = BitField ( 32 )
    s.type_ = BitField ( 1 )

  def mk_msg( s, data, addr, type_ ):
    msg       = s()
    msg.data  = data
    msg.addr  = addr
    msg.type_ = type_
    return msg

  def __str__( s ):
    return "d{}:a{}:t{}".format( s.data, s.addr, s.type_ )

class pageRankRespMsg( BitStructDefinition ):


  TYPE_READ = 0
  TYPE_WRITE = 1
  def __init__( s ):
    s.data  = BitField ( 32 )
    s.type_ = BitField ( 1 )

  def mk_msg( s, data, type_ ):
    msg       = s()
    msg.data  = data
    msg.type_ = type_
    return msg

  def __str__( s ):
    return "d{}:t{}".format( s.data, s.type_ )
