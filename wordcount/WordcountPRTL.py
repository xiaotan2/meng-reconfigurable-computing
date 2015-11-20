
from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemReqMsg, MemRespMsg
from MapperMsg  import MapperReqMsg, MapperRespMsg
from ReducerMsg import ReducerReqMsg, ReducerRespMsg
from SchedulerPRTL import *
from MapperPRTL    import *
from ReducerPRTL   import *

class WordcountPRTL( Model ):

  def __init__( s, mapper_num = 2, reducer_num = 1):

    # Interface

    s.wcreq        = InValRdyBundle  ( WordcountReqMsg() )
    s.wcresp       = OutValRdyBundle ( WordcountRespMsg() )

    s.memreq       = OutValRdyBundle ( MemReqMsg(8, 32, 32) )
    s.memresp      = InValRdyBundle  ( MemRespMsg(8, 32) )

    # Framework Components

    s.map      = MapperPRTL  [mapper_num]  ()
    s.red      = ReducerPRTL [reducer_num] ()
    s.sche     = SchedulerPRTL ()

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
      s.wcreq,           s.sche.in_,
      s.wcresp,          s.sche.out,
    )

  def line_trace(s):
    return s.sche.line_trace()       + " > " + \
           s.map[0].line_trace()        + " > " + \
           s.map[1].line_trace()        + " > " + \
           s.red[0].line_trace()   
