#======================================================================
# PageRank Functional Level Model
#======================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.fl   import InValRdyQueueAdapterFL, OutValRdyQueueAdapterFL
from numpy.random import random
from numpy      import sum, ones

class pageRankFL( Model ):

  # Constructor

  def __init__( s, numPage=6 ):

  # Interface

  s.req    = InValRdyBundle  ( pageRankReqMsg()  )
  s.resp   = OutValRdyBundle ( pageRankRespMsg() )

  # Concurrent block

  @s.tick_fl
  def block():
    req_msg = s.req_q.popleft()
    result = Bits( 32, req_msg[32:64] * req_msg[0:32], trunc=True )
    s.resp_q.append( result )

  # Line tracing

  def line_trace( s ):
    return "{}(){}".format( s.req, s.resp )
