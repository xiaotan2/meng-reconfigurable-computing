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
               stall_prob, latency, src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src       = TestSource    ( WordcountReqMsg(),  src_msgs,  src_delay  )
    s.wordcount = WordcountPRTL
    s.sink      = TestSink      ( WordcountRespMsg(), sink_msgs, sink_delay )
    s.mem       = TestMemory    ( MemMsg(8,32,32), 1, stall_prob, latency   )

    # Dump VCD
    if dump_vcd:
      s.wordcount.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.wordcount = TranslationTool( s.wordcount )

    # Connect
    s.connect( s.src.out,           s.wordcount.wcreq )
    s.connect( s.wordcount.wcresp,  s.sink.in_        )
    s.connect( s.wordcount.memreq,  s.mem.reqs[0]     )
    s.connect( s.wordcount.memresp, s.mem.resps[0]    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.src.line_trace()       + " > " + \
           s.wordcount.line_trace() + " > " + \
           s.sink.line_trace()    


#-------------------------------------------------------------------------
# make msgs
#-------------------------------------------------------------------------

def req( type, addr, data ):
  msg      = WordcountReqMsg()
  if type == 'rd': msg.type_ = WordcountReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = WordcountReqMsg.TYPE_WRITE
  msg.addr = addr
  msg.data = data
  return msg

def resp( type, data ):
  msg      = WordcountRespMsg()
  if type == 'rd': msg.type_ = WordcountReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = WordcountReqMsg.TYPE_WRITE
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
    req( 'wr', 0, 0      ), resp( 'wr', 0      ),
    req( 'rd', 0, 0      ), resp( 'rd', result ),
  ]


#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

very_basic_data = [ 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x02 ]
basic_data      = [ 0x12, 0x23, 0x45, 0x35, 0x41, 0xab, 0xc7, 0x8d, 0x41, 0xf5 ]

random_data = []
result_rdm  = 0
ref_rdm     = random.randint(0,0x1f)
for i in xrange(500):
  a = random.randint(0,0x1f)
  random_data.append(a)
  if ( a == ref_rdm ):
    result_rdm = result_rdm + 1

  


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                 "data            ref    result       stall  latency  src_delay  sink_delay" ),
  [ "vbasic_0x0x0", very_basic_data, 0x02,    2,           0,     0,       0,         0         ], 
  [ "basic_0x0x0",  basic_data,      0x41,    2,           0,     0,       0,         0         ],
  [ "random_0x0x0", random_data,     ref_rdm, result_rdm,  0,     0,       0,         0         ], 
])

#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( wordcount, test_params, dump_vcd, test_verilog=False ):

  data       = test_params.data
  ref        = test_params.ref
  result     = test_params.result
  data_bytes = struct.pack("<{}I".format(len(data)), *data)
  
  wordcount_protocol_msgs = gen_protocol_msgs( len(data), ref, result )
  wordcount_reqs          = wordcount_protocol_msgs[::2]
  wordcount_resps         = wordcount_protocol_msgs[1::2]

  th = TestHarness( wordcount, wordcount_reqs, wordcount_resps, 
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  th.mem.write_mem( 0x1000, data_bytes )
  run_sim( th, dump_vcd, max_cycles=5000 )
  
  
@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( WordcountPRTL(), test_params, dump_vcd )
