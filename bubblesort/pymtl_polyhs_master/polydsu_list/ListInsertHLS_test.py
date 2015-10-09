#===============================================================
# ListInsertHLS_test
#===============================================================

import pytest
import struct

from pymtl       import *
from pclib.test  import mk_test_case_table, run_sim
from pclib.test  import TestSource, TestSink

from xmem.TestMemoryOpaque import TestMemory
from ListInsertHLS         import ListInsertHLS

from xcel.XcelMsg      import XcelReqMsg, XcelRespMsg
from xmem.MemMsgFuture import MemMsg

#---------------------------------------------------------------
# TestHarness
#---------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, xcel, src_msgs, sink_msgs,
                stall_prob, latency, src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( XcelReqMsg(),  src_msgs,  src_delay  )
    s.xcel = xcel
    s.mem  = TestMemory ( MemMsg(8,32,32), 1, stall_prob, latency )
    s.sink = TestSink   ( XcelRespMsg(), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.xcel.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.xcel = TranslationTool( s.xcel )

    # Connect

    s.connect( s.src.out,       s.xcel.xcelreq )
    s.connect( s.xcel.memreq,   s.mem.reqs[0]  )
    s.connect( s.xcel.memresp,  s.mem.resps[0] )
    s.connect( s.xcel.xcelresp, s.sink.in_     )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.xcel.line_trace() + " | " + \
           s.mem.line_trace()  + " > " + \
           s.sink.line_trace()

#---------------------------------------------------------------
# make messages
#---------------------------------------------------------------

def req( type_, raddr, data ):
  msg = XcelReqMsg()

  if   type_ == 'rd': msg.type_ = XcelReqMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = XcelReqMsg.TYPE_WRITE

  msg.raddr = raddr
  msg.data  = data
  return msg

def resp( type_, data ):
  msg = XcelRespMsg()

  if   type_ == 'rd': msg.type_ = XcelRespMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = XcelRespMsg.TYPE_WRITE

  msg.data  = data
  return msg

#---------------------------------------------------------------
# Xcel Protocol
#---------------------------------------------------------------
# These are the source sink messages we need to configure the accelerator
# and wait for it to finish for a SINGLE insert operation.

def gen_xcel_protocol_msgs( pos, mem_pos, val ):
  return [
    req( 'wr', 1, pos     ), resp( 'wr', 0 ),
    req( 'wr', 2, mem_pos ), resp( 'wr', 0 ),
    req( 'wr', 3, val     ), resp( 'wr', 0 ),
    req( 'wr', 0, 0       ), resp( 'wr', 0 ),
    req( 'rd', 0, 0       ), resp( 'rd', mem_pos ),
  ]

#---------------------------------------------------------------
# Test 1: Insert Head
#---------------------------------------------------------------
test1_data = [
    0,    0,    0,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
]

test1_data_ref = [
    24,   36,   0,     # 0
    48,   24,   3,     # 12
    12,   0,    4,      # 24
    0,    48,   1,     # 36
    36,   12,   2,     # 48
]

#                             insert_at  mem  data
test1_msgs = gen_xcel_protocol_msgs( 0,   24,   4 ) + \
             gen_xcel_protocol_msgs( 24,  12,   3 ) + \
             gen_xcel_protocol_msgs( 12,  48,   2 ) + \
             gen_xcel_protocol_msgs( 48,  36,   1 )

#---------------------------------------------------------------
# Test 2: Insert Tail
#---------------------------------------------------------------
test2_data = test1_data

test2_data_ref = [
    48,   12,   0,     # 0
    0,    36,   1,     # 12
    36,   48,   3,     # 24
    12,   24,   2,     # 36
    24,   0,    4,     # 48
]

#                             insert_at  mem  data
test2_msgs = gen_xcel_protocol_msgs( 0,   12,   1 ) + \
             gen_xcel_protocol_msgs( 0,   36,   2 ) + \
             gen_xcel_protocol_msgs( 0,   24,   3 ) + \
             gen_xcel_protocol_msgs( 0,   48,   4 )

#---------------------------------------------------------------
# Test Case Table
#---------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                            "msgs          src sink stall lat  data         data_ref" ),
  [ "insert_head_0x0_0.0_0",    test1_msgs,   0,  0,   0.0,  0,   test1_data,  test1_data_ref ],
  [ "insert_head_3x5_0.0_0",    test1_msgs,   3,  5,   0.0,  0,   test1_data,  test1_data_ref ],
  [ "insert_head_3x14_0.5_4",   test1_msgs,   3, 14,   0.5,  4,   test1_data,  test1_data_ref ],
  [ "insert_tail_0x0_0.0_0",    test2_msgs,   0,  0,   0.0,  0,   test2_data,  test2_data_ref ],
  [ "insert_tail_3x5_0.0_0",    test2_msgs,   3,  5,   0.0,  0,   test2_data,  test2_data_ref ],
  [ "insert_tail_3x14_0.5_4",   test2_msgs,   3, 14,   0.5,  4,   test2_data,  test2_data_ref ],
])

#---------------------------------------------------------------
# run_test
#---------------------------------------------------------------

def run_test( xcel, test_params, dump_vcd, test_verilog=False ):

  # Convert test data into byte array

  data = test_params.data
  data_bytes = struct.pack("<{}I".format(len(data)),*data)

  # Protocol messages

  xreqs  = test_params.msgs[::2]
  xresps = test_params.msgs[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( xcel, xreqs, xresps,
                    test_params.stall, test_params.lat,
                    test_params.src, test_params.sink,
                    dump_vcd, test_verilog )

  # Load the data into the test memory

  th.mem.write_mem( 0x0000, data_bytes )

  # Run the test

  run_sim( th, dump_vcd, max_cycles=2000 )

  # Retrieve data from test memory

  result_bytes = th.mem.read_mem( 0x0000, len(data_bytes) )

  # Convert result bytes into list of ints

  result = list(struct.unpack("<{}I".format(len(data)),buffer(result_bytes)))

  # Compare result to sorted reference

  print result
  print test_params.data_ref
  assert result == test_params.data_ref

#---------------------------------------------------------------
# Test cases
#---------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_test( ListInsertHLS(), test_params, dump_vcd, test_verilog )

