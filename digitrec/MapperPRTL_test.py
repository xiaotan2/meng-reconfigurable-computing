#=========================================================================
# MapperPRTL_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink

from MapperPRTL import MapperPRTL
from MapperMsg  import MapperReqMsg, MapperRespMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, MapperPRTL, src_msgs, sink_msgs,
               src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src     = TestSource  ( MapperReqMsg(),  src_msgs,  src_delay  )
    s.mapper  = MapperPRTL ()
    s.sink    = TestSink    ( MapperRespMsg(), sink_msgs, sink_delay )

    # Dump VCD
    if dump_vcd:
      s.mapper.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.mapper = TranslationTool( s.mapper )

    # Connect
    s.connect( s.src.out,      s.mapper.req )
    s.connect( s.mapper.resp,  s.sink.in_   )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()     + " > " + \
           s.mapper.line_trace() + " > " + \
           s.sink.line_trace()    

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( data, type, digit ):
  msg       = MapperReqMsg()
  msg.data  = data
  msg.type_ = type
  msg.digit = digit
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, type, digit ):
  msg       = MapperRespMsg()
  msg.data  = data
  msg.type_ = type
  msg.digit = digit
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  mk_req_msg( 0x1034, 1, 4 ), None,
  mk_req_msg( 0x2015, 0, 4 ), mk_resp_msg( 0x4, 0, 4 ),
  mk_req_msg( 0x1f31, 0, 4 ), mk_resp_msg( 0x6, 0, 4 ),
  mk_req_msg( 0xf752, 0, 4 ), mk_resp_msg( 0xa, 0, 4 ),
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
  run_sim( TestHarness( MapperPRTL,
                        test_params.msgs[::2], test_params.msgs[3::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

