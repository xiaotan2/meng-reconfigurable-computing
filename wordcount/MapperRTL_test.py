#=========================================================================
# GcdUnitFL_test
#=========================================================================

import pytest
import random

from copy       import deepcopy

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from MapperMsg  import MapperReqMsg, MapperRespMsg
from MapperPRTL import MapperRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, MapperRTL, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src     = TestSource ( MapperReqMsg(), src_msgs,  src_delay  )
    s.mapper  = MapperRTL ()
    s.sink    = TestSink   ( MapperRespMsg(), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.mapper.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.mapper = TranslationTool( s.mapper )

    # Connect

    s.connect( s.src.out,  s.mapper.req  )
    s.connect( s.mapper.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.mapper.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( data, type ):
  msg = MapperReqMsg()
  msg.data = data
  msg.type_ = type
  return msg

#-------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( data, type ):
  msg = MapperRespMsg()
  msg.data = data
  msg.type_ = type
  return msg

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  mk_req_msg( 15,    1  ), mk_resp_msg( 1,  1  ),
  mk_req_msg( 3,     0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 0,     0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 27,    0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 21,    0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 15,    0  ), mk_resp_msg( 1,  0  ),
  mk_req_msg( 19,    0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 15,    0  ), mk_resp_msg( 1,  0  ),
  mk_req_msg( 250,   0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 5,     0  ), mk_resp_msg( 0,  0  ),
  mk_req_msg( 0xff,  0  ), mk_resp_msg( 0,  0  ),
]

#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random.seed(0xdeadbeef)
random_msgs = []
for j in xrange(20):
  target = random.randint( 0, 0xff )
  random_msgs.extend([ mk_req_msg( target, 1 ), mk_resp_msg( 1, 1 ) ])
  for i in xrange(20):
    a = random.randint(0,0xff)
    c = ( a == target )
    random_msgs.extend([ mk_req_msg( a, 0 ), mk_resp_msg( c, 0 ) ])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs       src_delay sink_delay"),
  [ "basic_0x0",  basic_msgs, 0,        0          ],
  [ "basic_5x0",  basic_msgs, 5,        0          ],
  [ "basic_0x5",  basic_msgs, 0,        5          ],
  [ "basic_3x9",  basic_msgs, 3,        9          ],
  [ "random_3x9", basic_msgs, 3,        9          ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( MapperRTL,
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

