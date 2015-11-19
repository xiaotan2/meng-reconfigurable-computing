#=========================================================================
# WordcountPRTL_test
#=========================================================================

import pytest
import random
import struct

from pymtl           import *
from pclib.test      import mk_test_case_table, run_sim
from pclib.test      import TestSource, TestSink
from pclib.test      import TestMemory
from pclib.ifcs      import MemMsg, MemReqMsg, MemRespMsg

from WordcountPRTL   import WordcountPRTL
from WordcountMsg    import WordcountReqMsg, WordcountRespMsg


#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, WordcountPRTL, src_msgs, sink_msgs,
               src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src       = TestSource    ( WordcountReqMsg(),  src_msgs,  src_delay  )
    s.wordcount = WordcountPRTL ()
    s.sink      = TestSink      ( WordcountRespMsg(), sink_msgs, sink_delay )

    # Dump VCD
    if dump_vcd:
      s.wordcount.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.wordcount = TranslationTool( s.wordcount )

    # Connect
    s.connect( s.src.out,        s.wordcount.req )
    s.connect( s.wordcount.resp, s.sink.in_      )
    

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()       + " > " + \
           s.wordcount.line_trace() + " > " + \
           s.sink.line_trace()    

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( data, type ):
  msg       = ReducerReqMsg()
  msg.data  = data
  msg.type_ = type
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  mk_req_msg( 1, 1 ), 1, 
  mk_req_msg( 0, 1 ), 0,
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
  run_sim( TestHarness( WordcountPRTL,
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

