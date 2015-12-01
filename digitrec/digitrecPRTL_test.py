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

from digitrecPRTL    import digitrecPRTL
from digitrecMsg     import digitrecReqMsg, digitrecRespMsg


#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, digitrecPRTL, src_msgs, sink_msgs,
               stall_prob, latency, src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src       = TestSource    ( digitrecReqMsg(),  src_msgs,  src_delay  )
    s.di        = digitrecPRTL
    s.sink      = TestSink      ( digitrecRespMsg(), sink_msgs, sink_delay )
    s.mem       = TestMemory    ( MemMsg(8,32,56), 1, stall_prob, latency   )

    # Dump VCD
    if dump_vcd:
      s.di.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.di = TranslationTool( s.wordcount )

    # Connect
    s.connect( s.src.out,           s.di.direq )
    s.connect( s.di.diresp,         s.sink.in_        )
    s.connect( s.di.memreq,         s.mem.reqs[0]     )
    s.connect( s.di.memresp,        s.mem.resps[0]    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()       + " > " + \
           s.di.line_trace() + " > " + \
           s.sink.line_trace()    


#-------------------------------------------------------------------------
# make msgs
#-------------------------------------------------------------------------

def req( type, addr, data ):
  msg      = digitrecReqMsg()
  if type == 'rd': msg.type_ = digitrecReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = digitrecReqMsg.TYPE_WRITE
  msg.addr = addr
  msg.data = data
  return msg

def resp( type, data ):
  msg      = digitrecRespMsg()
  if type == 'rd': msg.type_ = digitrecReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = digitrecReqMsg.TYPE_WRITE
  msg.data = data
  return msg
  
#-------------------------------------------------------------------------
# Protocol 
#-------------------------------------------------------------------------

def gen_protocol_msgs( size, ref, result ):
  return [
    req( 'wr', 1, 0x1000 ), resp( 'wr', 0      ),
    req( 'wr', 2, size   ), resp( 'wr', 0      ),
    req( 'wr', 3, ref    ), resp( 'wr', 0      ),
    req( 'wr', 4, 0      ), resp( 'wr', 0      ),
    req( 'wr', 0, 0      ), resp( 'wr', 0      ),
    req( 'rd', 0, 0      ), resp( 'rd', result ),
  ]


#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

training_data = []
for i in xrange(10):
  filename = 'data/training_set_' + str(i) + '.dat'
  with open(filename, 'r') as f:
    for L in f:
      training_data.append(int(L.replace(',\n',''), 16))


small_train_data = []
for i in xrange(10):
  filename = 'data/training_set_' + str(i) + '.dat'
  with open(filename, 'r') as f:
    count = 0
    for L in f:
      small_train_data.append(int(L.replace(',\n',''), 16))
      count += 1
      if count >=10:
        break


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------
test_case_table = mk_test_case_table([
  (                  "data             ref              result       stall  latency  src_delay  sink_delay" ),
  [ "basic1_0x0x0",  training_data,    0x3041060800,    1,           0,     0,       0,         0         ],
  [ "small4_0x0x0",  small_train_data, 0x41c3830408,    1,           0,     0,       0,         0         ],
])

#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( digitrec, test_params, dump_vcd, test_verilog=False ):

  data       = test_params.data
  ref        = test_params.ref
  result     = test_params.result
  data_bytes = struct.pack("<{}Q".format(len(data)), *data)
  
  digitrec_protocol_msgs = gen_protocol_msgs( len(data), ref, result )
  digitrec_reqs          = digitrec_protocol_msgs[::2]
  digitrec_resps         = digitrec_protocol_msgs[1::2]

  th = TestHarness( digitrec, digitrec_reqs, digitrec_resps, 
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  th.mem.write_mem( 0x1000, data_bytes )
  run_sim( th, dump_vcd, max_cycles=5000 )
  
  
@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( digitrecPRTL(), test_params, dump_vcd )
