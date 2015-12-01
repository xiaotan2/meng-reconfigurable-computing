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
  msg       = FindMaxReqMsg( data )
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, idx ):
  msg       = FindMaxRespMsg( data, idx )
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  mk_req_msg( 0xa ), None,
  mk_req_msg( 0xb ), None,
  mk_req_msg( 0xc ), mk_resp_msg( 0xc, 0x3 ),
]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs       src_delay  sink_delay" ),
  [ "basic_0x0",  basic_msgs, 0,         0           ], 
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( FindMaxPRTL,
                        test_params.msgs[::2], test_params.msgs[5::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

