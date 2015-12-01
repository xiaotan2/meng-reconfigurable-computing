#=========================================================================
# FindMax_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink

from FindMaxPRTL import FindMaxPRTL
from FindMaxMsg  import FindMaxReqMsg, FindMaxRespMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, FindMaxPRTL, src_msgs, sink_msgs,
               src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src     = TestSource  ( FindMaxReqMsg(),  src_msgs,  src_delay  )
    s.findmax = FindMaxPRTL ()
    s.sink    = TestSink    ( FindMaxRespMsg(), sink_msgs, sink_delay )

    # Dump VCD
    if dump_vcd:
      s.findmax.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.findmax = TranslationTool( s.findmax )

    # Connect
    s.connect( s.src.out,      s.findmax.req )
    s.connect( s.findmax.resp, s.sink.in_    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()     + " > " + \
           s.findmax.line_trace() + " > " + \
           s.sink.line_trace()    

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( data ):
  msg       = FindMaxReqMsg()
  msg.data  = data
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, idx ):
  msg       = FindMaxRespMsg()
  msg.data  = data
  msg.idx   = idx
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs_2 = [
  mk_req_msg( 0xa ), None,
  mk_req_msg( 0xb ), None,
  mk_req_msg( 0xc ), mk_resp_msg( 0xc, 0x2 ),
]

basic_msgs_0 = [
  mk_req_msg( 0xc ), None,
  mk_req_msg( 0xb ), None,
  mk_req_msg( 0xa ), mk_resp_msg( 0xc, 0x0 ),
]

basic_msgs_1 = [
  mk_req_msg( 0xb ), None,
  mk_req_msg( 0xc ), None,
  mk_req_msg( 0xa ), mk_resp_msg( 0xc, 0x1 ),
]

basic_msgs_same = [
  mk_req_msg( 0xc ), None,
  mk_req_msg( 0xc ), None,
  mk_req_msg( 0xc ), mk_resp_msg( 0xc, 0x0 ),
]


basic_msgs = [
  mk_req_msg( 0x32 ), None,
  mk_req_msg( 0x01 ), None,
  mk_req_msg( 0x22 ), mk_resp_msg( 0x32, 0x0 ),
  mk_req_msg( 0x00 ), None,
  mk_req_msg( 0x22 ), None,
  mk_req_msg( 0x0a ), mk_resp_msg( 0x22, 0x1 ),
  mk_req_msg( 0x19 ), None,
  mk_req_msg( 0x11 ), None,
  mk_req_msg( 0x24 ), mk_resp_msg( 0x24, 0x2 ),
  mk_req_msg( 0x0  ), None,
  mk_req_msg( 0x0  ), None,
  mk_req_msg( 0x0  ), mk_resp_msg( 0x0,  0x0 ),
]
#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random.seed(0xdeadbeef)
random_msgs = []
for j in xrange(20):
  knn_value_0 = random.randint( 0, 0x32 )
  random_msgs.extend([ mk_req_msg( knn_value_0 ), None ])
  knn_value_1 = random.randint( 0, 0x32 )
  random_msgs.extend([ mk_req_msg( knn_value_1 ), None ])
  knn_value_2 = random.randint( 0, 0x32 )
  if (knn_value_0 > knn_value_1):
    max_value = knn_value_0
    max_idx   = 0
  else :
    max_value = knn_value_1
    max_idx   = 1
  if (knn_value_2 > max_value):
    max_value = knn_value_2
    max_idx   = 2
   
  random_msgs.extend([ mk_req_msg( knn_value_2 ), mk_resp_msg( max_value, max_idx )])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs         src_delay  sink_delay" ),
  [ "basic_0",    basic_msgs_0, 0,         0           ], 
  [ "basic_1",    basic_msgs_1, 0,         0           ], 
  [ "basic_2",    basic_msgs_2, 0,         0           ], 
  [ "basic_same", basic_msgs_same, 0,         0           ], 
  [ "basic",      basic_msgs,   0,         0           ], 
  [ "random",     random_msgs,  0,         0           ], 
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( FindMaxPRTL,
                        test_params.msgs[::2], test_params.msgs[5::6],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

