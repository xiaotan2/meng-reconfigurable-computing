
from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.ifcs    import MemReqMsg, MemRespMsg
from SchedulerPRTL import *
from MapperPRTL    import *
from ReducerPRTL   import *
from MergerPRTL   import *

import math

DATA_BITS  = 49
DIGIT      = 10
TRAIN_DATA = 60

class digitrecPRTL( Model ):

  def __init__( s, mapper_num = 30, reducer_num = 10, k = 3, nbits = 6 ):

    sum_nbits = int( math.ceil( math.log( (2**nbits-1)*k, 2 ) ) )

    # Interface

    s.direq        = InValRdyBundle  ( digitrecReqMsg() )
    s.diresp       = OutValRdyBundle ( digitrecRespMsg() )

    s.memreq       = OutValRdyBundle ( MemReqMsg(8, 32, 64) )
    s.memresp      = InValRdyBundle  ( MemRespMsg(8, 64) )

    # Framework Components

    s.map          = MapperPRTL  [mapper_num]  ()
    s.red          = ReducerPRTL [reducer_num] ( mapper_num/reducer_num, nbits, k, 50 )
    s.mer          = MergerPRTL                ( reducer_num, sum_nbits )
    s.sche         = SchedulerPRTL             (mapper_num = mapper_num, reducer_num = reducer_num)

    # Assign Register File to Mapper

    s.train_data = m = RegisterFile [DIGIT] ( dtype=Bits( DATA_BITS ),
                       nregs=TRAIN_DATA, rd_ports=mapper_num/DIGIT, wr_ports=1, const_zero=False )

    # Connect Registerfile read port to Mapper
    for i in xrange(DIGIT):
      for j in xrange(mapper_num/DIGIT):
        s.connect(
          m[i].rd_data[j], s.map[j*10+i].in0,
        )

    # Connect Registerfile write port to Scheduler
    for i in xrange(DIGIT):
      s.connect_dict({
        m[i].wr_addr : s.sche.regf_addr[i],
        m[i].wr_data : s.sche.regf_data[i],
        m[i].wr_en   : s.sche.regf_wren[i],
      })

    # Connect Registerfile rd port to Scheduler
    for i in xrange( DIGIT ):
      for j in xrange( mapper_num/reducer_num ):
        s.connect(
          m[i].rd_addr[j], s.sche.regf_rdaddr[j],
        )

    # Connect Mapper test data port to Scheduler
    for i in xrange(mapper_num):
      s.connect(s.sche.map_req[i], s.map[i].in1)

    # Connect Mapper Output to Reducer
    # for 3 mapper : 1 reducer, mapper 0, 10, 20 connect to reducer 0, etc
    for i in xrange(reducer_num):
      for j in xrange(mapper_num/reducer_num):
        s.connect_pairs (
          s.map[i+10*j].out,  s.red[i].in_[j],
        )

    # Connect rst signal from Scheduler to Reducer
    for i in xrange( reducer_num ):
      s.connect_pairs( 
        s.sche.red_rst, s.red[i].rst,
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

  def line_trace(s, mapper_num = 30, reducer_num=10):

    mapper = ""
#    for i in xrange(mapper_num):
#      mapper = mapper + s.map[i].line_trace() + " > "

    reducer = ""
#    for i in xrange(reducer_num):
#      reducer = reducer + s.red[i].line_trace() + " > "

    return s.sche.line_trace()       + " > " + \
           mapper                    + " > " + \
           reducer
