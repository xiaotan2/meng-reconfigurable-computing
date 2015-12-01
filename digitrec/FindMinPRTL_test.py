#=========================================================================
# FindMin_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink

from FindMinPRTL import FindMinPRTL
from FindMinMsg  import FindMinReqMsg, FindMinRespMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, FindMinPRTL, src_msgs, sink_msgs,
               src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src     = TestSource  ( FindMinReqMsg(),  src_msgs,  src_delay  )
    s.findmax = FindMinPRTL ()
    s.sink    = TestSink    ( FindMinRespMsg(), sink_msgs, sink_delay )

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
  msg       = FindMinReqMsg()
  msg.data  = data
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, digit ):
  msg       = FindMinRespMsg()
  msg.data  = data
  msg.digit = digit
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs_1 = [
  mk_req_msg( 0x5 ), None,
  mk_req_msg( 0x1 ), None,
  mk_req_msg( 0x4 ), None,
  mk_req_msg( 0x5 ), None,
  mk_req_msg( 0x9 ), None,
  mk_req_msg( 0x2 ), None,
  mk_req_msg( 0x3 ), None,
  mk_req_msg( 0x7 ), None,
  mk_req_msg( 0x2 ), None,
  mk_req_msg( 0xc ), mk_resp_msg( 0x1, 0x1 ),
]


#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random.seed(0xdeadbeef)
random_msgs = []
for j in xrange(50):

  min_value = 0xff
  min_idx   = 0
  for i in xrange(10) :
    knn_value = random.randint( 0, 0x96 )
    if ( i < 9 ):
      random_msgs.extend([ mk_req_msg( knn_value ), None ])
    if ( knn_value < min_value ):
      min_value = knn_value
      min_idx   = i

  random_msgs.extend([ mk_req_msg( knn_value ), mk_resp_msg( min_value, min_idx )])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs         src_delay  sink_delay" ),
  [ "basic_1",    basic_msgs_1, 0,         0           ], 
  [ "basic_ranom",random_msgs,  0,         0           ], 
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( FindMinPRTL,
                        test_params.msgs[::2], test_params.msgs[19::20],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

