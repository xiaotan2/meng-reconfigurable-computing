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
    s.mem       = TestMemory    ( MemMsg(8,32,64), 1, stall_prob, latency   )

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
    return s.di.line_trace(mapper_num = 30, reducer_num=10)
#s.src.line_trace()       + " > " + \
#           s.di.line_trace(mapper_num=30, reducer_num=10) + " > " + \
#           s.sink.line_trace()    


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

def gen_protocol_msgs( size, result ):
  return [
    req( 'wr', 1, 0x1000 ), resp( 'wr', 0      ),
    req( 'wr', 2, size   ), resp( 'wr', 0      ),
    req( 'wr', 0, 0      ), resp( 'wr', 0      ),
    req( 'rd', 0, 0      ), resp( 'rd', result ),
  ]


#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

test_data = []
result_data = []
data      = []
with open('data/testing_set.dat', 'r') as f:
  for L in f:
    L = L.replace('\n','')
    data.append(L.split(','))
  for row in data:
    test_data.append(int(row[0], 16))
    result_data.append(int(row[1]))

small_test_data = []
small_result_data = []
for i in xrange(2):
  small_test_data.append(int(data[i][0],16))
  small_result_data.append(int(data[i][1]))

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------
test_case_table = mk_test_case_table([
  (                  "data            result       stall  latency  src_delay  sink_delay" ),
  [ "basic_0x0x0",   test_data,       1,           0,     0,       0,         0         ],
  [ "small_0x0x0",   small_test_data, 1,           0,     0,       0,         0         ],
])

#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( digitrec, test_params, dump_vcd, test_verilog=False ):

  data       = test_params.data
  result     = test_params.result
  data_bytes = struct.pack("<{}Q".format(len(data)), *data)
  
  digitrec_protocol_msgs = gen_protocol_msgs( len(data), result )
  digitrec_reqs          = digitrec_protocol_msgs[::2]
  digitrec_resps         = digitrec_protocol_msgs[1::2]

  th = TestHarness( digitrec, digitrec_reqs, digitrec_resps, 
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  th.mem.write_mem( 0x1000, data_bytes )
  run_sim( th, dump_vcd, max_cycles=3000 )

  # Retrieve result from test memory
  result_bytes = struct.pack("<{}I".format(len(result_data)),*result_data )
  result_bytes = th.mem.read_mem( 0x2000, len(result_bytes) )
  result_list  = list(struct.unpack("<{}I".format(len(result_data)), buffer(result_bytes)))

  # Calculate error rate and print it
  accuracy = 0
  for i in xrange(len(result_list)):
    if result_list[i] == result_data[i]:
      accuracy = accuracy + 1
  error_rate = (len(result_list)-accuracy)/len(result_list)
  print("Overall Error Rate is: " + str(error_rate*100) + "%")

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( digitrecPRTL(mapper_num = 30, reducer_num = 10), test_params, dump_vcd )
