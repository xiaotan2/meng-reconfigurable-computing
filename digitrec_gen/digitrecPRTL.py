from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.ifcs    import MemReqMsg, MemRespMsg
from MapperMsg     import MapperReqMsg, MapperRespMsg
from ReducerMsg    import ReducerReqMsg, ReducerRespMsg
from SchedulerPRTL import *
from MapperPRTL    import *
from ReducerPRTL   import *

class digitrecPRTL( Model ):

  def __init__( s, mapper_num = 10, reducer_num = 1):

    # Interface

    s.direq        = InValRdyBundle  ( digitrecReqMsg() )
    s.diresp       = OutValRdyBundle ( digitrecRespMsg() )

    s.memreq       = OutValRdyBundle ( MemReqMsg(8, 32, 56) )
    s.memresp      = InValRdyBundle  ( MemRespMsg(8, 56) )

    # Framework Components

    s.map          = MapperPRTL  [mapper_num]  ()
    s.red          = ReducerPRTL [reducer_num] ()
    s.sche         = SchedulerPRTL ()

    # Connect Framework Components

    for i in xrange(mapper_num):
      s.connect_pairs (
        s.sche.map_req[i],  s.map[i].req,
        s.sche.map_resp[i], s.map[i].resp,
      )

    for i in xrange(reducer_num):
      s.connect_pairs (
        s.sche.red_req[i],  s.red[i].req,
        s.sche.red_resp[i], s.red[i].resp,
      )

    s.connect_pairs (
      s.sche.gmem_req,   s.memreq,
      s.sche.gmem_resp,  s.memresp,
      s.direq,           s.sche.in_,
      s.diresp,          s.sche.out,
    )

  def line_trace(s, mapper_num = 10, reducer_num = 1):

    mapper = ""
    for i in xrange(mapper_num):
      mapper = mapper + s.map[i].line_trace() + " > "

    reducer = ""
    for i in xrange(reducer_num):
      reducer = reducer + s.red[i].line_trace() + " > "

    return s.sche.line_trace()       + " > " + \
           mapper                    + " > " + \
           reducer

