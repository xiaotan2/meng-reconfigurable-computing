
from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.ifcs    import MemReqMsg, MemRespMsg
from MapperMsg     import MapperReqMsg, MapperRespMsg
from SchedulerPRTL import *
from MapperPRTL    import *
from ReducerPRTL   import *
from MergerPRTL   import *

DATA_BITS  = 49
DIGIT      = 10
TRAIN_DATA = 1800

class digitrecPRTL( Model ):

  def __init__( s, mapper_num = 10, reducer_num = 1):

    # Interface

    s.direq        = InValRdyBundle  ( digitrecReqMsg() )
    s.diresp       = OutValRdyBundle ( digitrecRespMsg() )

    s.memreq       = OutValRdyBundle ( MemReqMsg(8, 32, 8) )
    s.memresp      = InValRdyBundle  ( MemRespMsg(8, 56) )

    # Framework Components

    s.map          = MapperPRTL  [mapper_num]  ()
    s.red          = ReducerPRTL [reducer_num] ()
    s.mer          = MergerPRTL    ()
    s.sche         = SchedulerPRTL ()

    # Assign Register File to Mapper

    s.train_data = m = RegisterFile [DIGIT] ( dtype=Bits( DATA_BITS ),
                       nregs=TRAIN_DATA, rd_ports=mapper_num/DIGIT, wr_ports=1, const_zero=False )

    # Connect Registerfile read port to Mapper
    for i in xrange(DIGIT):
      for j in xrange(mapper_num/DIGIT):
        s.connect_dict({
          m[i].rd_addr[j] : s.map[j*10+i].rd_addr,
          m[i].rd_data[j] : s.map[j*10+i].rd_data,
        })

    # Connect Registerfile write port to Scheduler
    for i in xrange(DIGIT):
      s.connect_dict({
        m[i].wr_addr[0] : s.sche.regf_addr[i],
        m[i].wr_data[0] : s.sche.regf_data[i],
        m[i].wr_en      : s.sche.regf_wren[i],
      })

    # Connect Mapper Request to Scheduler
    for i in xrange(mapper_num):
      s.connect_pairs (
        s.sche.map_req[i],  s.map[i].req,
      )

    # Connect Mapper Output to Reducer
    # for 3 mapper : 1 reducer, mapper 0, 10, 20 connect to reducer 0, etc
    for i in xrange(reducer_num):
      for j in xrange(mapper_num/reducer_num):
        s.connect_pairs (
          s.map[i+10*j].out,  s.red[i].in_[j],
        )

    # Connect Reducer Output to Merger
    for i in xrange(reducer_num):
      s.connect_pairs ( s.red[i].out, s.mer.in_[i] )

    # Connect Merger output to Scheduler
    s.connect(s.mer.out, s.sche.merger_resp)

    # Connect global memory and top level to scheduler
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
