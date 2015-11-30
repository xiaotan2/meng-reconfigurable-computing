#=========================================================================
# ReducerPRLT_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink

from ReducerPRTL import ReducerPRTL
from ReducerMsg  import ReducerReqMsg, ReducerRespMsg

from pclib.test  import TestMemory
from pclib.ifcs  import MemMsg, MemReqMsg, MemRespMsg

MEM_DATA_SIZE = 16

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, ReducerPRTL, src_msgs, sink_msgs,
                stall_prob, latency, src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src     = TestSource  ( ReducerReqMsg(),  src_msgs,  src_delay  )
    s.reducer = ReducerPRTL
    s.sink    = TestSink    ( ReducerRespMsg(), sink_msgs, sink_delay )
    s.mem     = TestMemory  ( MemMsg(8,20, MEM_DATA_SIZE), 1, stall_prob, latency )

    # Dump VCD
    if dump_vcd:
      s.reducer.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.reducer = TranslationTool( s.reducer     )

    # Connect
    s.connect( s.src.out,           s.reducer.req     )
    s.connect( s.reducer.resp,      s.sink.in_        )
    s.connect( s.reducer.mem_req,    s.mem.reqs[0]     )
    s.connect( s.reducer.mem_resp,   s.mem.resps[0]    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()     + " > " + \
           s.reducer.line_trace() + " > " + \
           s.sink.line_trace()    

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( data, digit, type_ ):
  msg       = ReducerReqMsg()
  msg.data  = data
  msg.digit = digit
  msg.type_ = type_
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, digit, type_ ):
  msg       = ReducerRespMsg()
  msg.data  = data
  msg.digit = digit
  msg.type_ = type_
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  mk_req_msg( 0, 0, 1 ), mk_resp_msg( 0, 0, 1 ), 
]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs       stall     latency    src_delay  sink_delay" ),
  [ "basic_0x0",  basic_msgs, 0,        0,         0,         0,          ], 
])



#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( reducer, test_params, dump_vcd, test_verilog=False ):

  reducer_reqs   = test_params.msgs[::2]
  reducer_resps  = test_params.msgs[1::2]

  th = TestHarness( reducer, reducer_reqs, reducer_resps,
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  run_sim( th, dump_vcd, max_cycles=50 )


@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( ReducerPRTL(), test_params, dump_vcd )

