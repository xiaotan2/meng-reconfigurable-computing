#=========================================================================
# PolyDsuListInorderPipeline_tests
#=========================================================================

import pytest
import struct

from pymtl             import *
from pclib.test        import TestSource, TestSink, mk_test_case_table

from PolyDsuListInorderPipeline import PolyDsuListInorderPipeline

from xmem.MemMsgFuture     import MemMsg
from xmem.TestMemoryOpaque import TestMemory
from polydsu.PolyDsuMsg    import PolyDsuReqMsg, PolyDsuRespMsg

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, model,
                src_xcel_msgs, sink_xcel_msgs,
                src_delay,     sink_delay,
                stall_prob,    latency,
                dump_vcd=False ):

    # Interfaces
    mem_ifc  = MemMsg(8,32,32)

    # Instantiate Models
    s.src   = TestSource ( PolyDsuReqMsg(), src_xcel_msgs, src_delay )

    s.model = model()

    s.sink  = TestSink ( PolyDsuRespMsg(), sink_xcel_msgs, sink_delay )

    s.mem   = TestMemory ( mem_ifc, 1, stall_prob, latency )

    # Connect
    s.connect( s.model.xcelreq,  s.src.out  )
    s.connect( s.model.xcelresp, s.sink.in_ )

    s.connect( s.model.memreq,  s.mem.reqs[0]  )
    s.connect( s.model.memresp, s.mem.resps[0] )

  def done( s ):
    return s.src.done & s.sink.done

  def line_trace( s ):
    return s.model.line_trace()

#-------------------------------------------------------------------------
# run_io_pipe_test
#-------------------------------------------------------------------------
def run_io_pipe_test( model, mem_array, test_params, dump_vcd = None ):

  # Elaborate
  model.vcd_file = dump_vcd
  model.elaborate()

  # Create a simulator
  sim = SimulationTool( model )

  # Load the memory
  if mem_array:
    model.mem.write_mem( mem_array[0], mem_array[1] )

  # Run simulation
  sim.reset()
  print

  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()
  sim.print_line_trace()
  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer
  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Check the memory for insert tests
  if test_params.insert:

    # Retrieve data from test memory
    result_bytes = model.mem.read_mem( 0x0000, len(mem_array[1]) )

    # Convert result bytes into list of ints
    result = list(struct.unpack("<{}I".format( len(mem_array[1])/4 ),buffer(result_bytes)))

    # Compare result to the reference
    assert result == test_params.ref_data

#-------------------------------------------------------------------------
# Utility functions for creating arrays formatted for memory loading.
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
# Utility functions for creating arrays formatted for memory loading.
#-------------------------------------------------------------------------
# mem_array_int
def mem_array_int( base_addr, data ):
  bytes = struct.pack( "<{}i".format( len(data) ), *data )
  return [base_addr, bytes]

#-------------------------------------------------------------------------
# Helper functions for Test xcel_src/xcel_sink messages
#-------------------------------------------------------------------------

dsu_req   = PolyDsuReqMsg().mk_dsu_msg
dsu_resp  = PolyDsuRespMsg().mk_dsu_msg

def dsu_req_rd( ds_id, opq, addr, data ):
  return dsu_req( ds_id, opq, PolyDsuReqMsg.TYPE_GET, addr, data, 0 )

def dsu_req_wr( ds_id, opq, addr, data ):
  return dsu_req( ds_id, opq, PolyDsuReqMsg.TYPE_SET, addr, data, 0 )

def dsu_req_inc( ds_id, opq, addr, data ):
  return dsu_req( ds_id, opq, PolyDsuReqMsg.TYPE_INCR, addr, data, 0 )

def dsu_req_dec( ds_id, opq, addr, data ):
  return dsu_req( ds_id, opq, PolyDsuReqMsg.TYPE_DECR, addr, data, 0 )

def dsu_req_cfg( id_, opq, addr, data, ds_id ):
  return dsu_req( id_, opq, PolyDsuReqMsg.TYPE_CFG, addr, data, ds_id )

def dsu_resp_rd( ds_id, opq, addr, data ):
  return dsu_resp( ds_id, opq, PolyDsuRespMsg.TYPE_GET, addr, data )

def dsu_resp_wr( ds_id, opq, addr, data ):
  return dsu_resp( ds_id, opq, PolyDsuRespMsg.TYPE_SET, addr, data )

def dsu_resp_inc( ds_id, opq, addr, data ):
  return dsu_resp( ds_id, opq, PolyDsuRespMsg.TYPE_INCR, addr, data )

def dsu_resp_dec( ds_id, opq, addr, data ):
  return dsu_resp( ds_id, opq, PolyDsuRespMsg.TYPE_DECR, addr, data )

def dsu_resp_cfg( id_, opq, addr, data ):
  return dsu_resp( id_, opq, PolyDsuRespMsg.TYPE_CFG, addr, data )

xcel_req  = PolyDsuReqMsg().mk_xcel_msg
xcel_resp = PolyDsuRespMsg().mk_xcel_msg

MTX = PolyDsuReqMsg.TYPE_MTX
MFX = PolyDsuReqMsg.TYPE_MFX

#-------------------------------------------------------------------------
# Memory array and messages to test list of integers
#-------------------------------------------------------------------------

# preload the memory to known values
list_int_mem = mem_array_int( 0,
                                [   #metadata
                                    0x00040000,
                                    # prev next value
                                         4, 16,     1,
                                         4, 28,     2,
                                        16, 40,     3,
                                        28, 0,      4,
                                ]
                             )

# messages that assume memory is preloaded and test for the case using the
# data structure with an id value to be 0
list_int_msgs = [
  # list-iterator operations
  #               id opq  addr  data                     id opq addr data
  dsu_req_rd ( 0x400,  0,    4,    0 ), dsu_resp_rd ( 0x400,  0,   4,   1 ),
  dsu_req_rd ( 0x400,  0,   16,    0 ), dsu_resp_rd ( 0x400,  0,  16,   2 ),
  dsu_req_rd ( 0x400,  0,   28,    0 ), dsu_resp_rd ( 0x400,  0,  28,   3 ),
  dsu_req_rd ( 0x400,  0,   40,    0 ), dsu_resp_rd ( 0x400,  0,  40,   4 ),

  dsu_req_inc( 0x400,  0,    4,    0 ), dsu_resp_inc( 0x400,  0,  16,   0 ),
  dsu_req_inc( 0x400,  0,   16,    0 ), dsu_resp_inc( 0x400,  0,  28,   0 ),
  dsu_req_inc( 0x400,  0,   28,    0 ), dsu_resp_inc( 0x400,  0,  40,   0 ),
  dsu_req_inc( 0x400,  0,   40,    0 ), dsu_resp_inc( 0x400,  0,   0,   0 ),

  dsu_req_dec( 0x400,  0,    4,    0 ), dsu_resp_dec( 0x400,  0,   4,   0 ),
  dsu_req_dec( 0x400,  0,   16,    0 ), dsu_resp_dec( 0x400,  0,   4,   0 ),
  dsu_req_dec( 0x400,  0,   28,    0 ), dsu_resp_dec( 0x400,  0,  16,   0 ),
  dsu_req_dec( 0x400,  0,   40,    0 ), dsu_resp_dec( 0x400,  0,  28,   0 ),

  dsu_req_wr ( 0x400,  0,    4,    5 ), dsu_resp_wr ( 0x400,  0,   4,   0 ),
  dsu_req_wr ( 0x400,  0,   16,    6 ), dsu_resp_wr ( 0x400,  0,  16,   0 ),
  dsu_req_wr ( 0x400,  0,   28,    7 ), dsu_resp_wr ( 0x400,  0,  28,   0 ),
  dsu_req_wr ( 0x400,  0,   40,    8 ), dsu_resp_wr ( 0x400,  0,  40,   0 ),

  dsu_req_rd ( 0x400,  0,    4,    0 ), dsu_resp_rd ( 0x400,  0,   4,   5 ),
  dsu_req_rd ( 0x400,  0,   16,    0 ), dsu_resp_rd ( 0x400,  0,  16,   6 ),
  dsu_req_rd ( 0x400,  0,   28,    0 ), dsu_resp_rd ( 0x400,  0,  28,   7 ),
  dsu_req_rd ( 0x400,  0,   40,    0 ), dsu_resp_rd ( 0x400,  0,  40,   8 ),

]

#---------------------------------------------------------------
# Test 1: Insert Head
#---------------------------------------------------------------

insert_mem = mem_array_int( 0,
  [
    0,    0,    0,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
    0xff, 0xff, 0xff,
  ]
)

insert_head_ref = [
    24,   36,   0,     # 0
    48,   24,   3,     # 12
    12,   0,    4,     # 24
    0,    48,   1,     # 36
    36,   12,   2,     # 48
  ]

insert_head_msgs = [
  # insert messages
  #               id opq      opc raddr rdata                     id  opq  opc  rdata
  xcel_req   ( 0x400,  0, MTX, 1,     0 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    24 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     4 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  24 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,    24 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    12 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     3 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  12 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,    12 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    48 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     2 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  48 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,    48 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    36 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     1 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  36 ), # result = mem_pos

]

#---------------------------------------------------------------
# Test 2: Insert Tail
#---------------------------------------------------------------

insert_tail_ref = [
    48,   12,   0,     # 0
    0,    36,   1,     # 12
    36,   48,   3,     # 24
    12,   24,   2,     # 36
    24,   0,    4,     # 48
]

insert_tail_msgs = [
  # insert messages
  #               id opq     opc raddr rdata                     id  opq    opc  rdata
  xcel_req   ( 0x400,  0, MTX, 1,     0 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    12 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     1 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  12 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,     0 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    36 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     2 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  36 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,     0 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    24 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     3 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  24 ), # result = mem_pos

  xcel_req   ( 0x400,  0, MTX, 1,     0 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # pos
  xcel_req   ( 0x400,  0, MTX, 2,    48 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX, 3,     4 ), xcel_resp   ( 0x400,   0, MTX,   0 ), # val
  xcel_req   ( 0x400,  0, MFX, 0,     0 ), xcel_resp   ( 0x400,   0, MFX,  48 ), # result = mem_pos

]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                          "msgs             src sink stall lat mem           insert ref_data"       ),
  [ "list_int_0x0_0.0_0",    list_int_msgs,    0,  0,   0.0,  0,  list_int_mem, False, None            ],
  [ "list_int_5x0_0.5_0",    list_int_msgs,    5,  0,   0.5,  0,  list_int_mem, False, None            ],
  [ "list_int_0x5_0.0_4",    list_int_msgs,    0,  5,   0.0,  4,  list_int_mem, False, None            ],
  [ "list_int_3x9_0.0_0",    list_int_msgs,    3,  9,   0.0,  0,  list_int_mem, False, None            ],
  [ "list_int_3x9_0.5_3",    list_int_msgs,    3,  9,   0.5,  3,  list_int_mem, False, None            ],
  [ "insert_head_0x0_0.0_0", insert_head_msgs, 0,  0,   0.0,  0,  insert_mem,   True,  insert_head_ref ],
  [ "insert_head_5x0_0.5_0", insert_head_msgs, 5,  0,   0.5,  0,  insert_mem,   True,  insert_head_ref ],
  [ "insert_head_0x5_0.0_4", insert_head_msgs, 0,  5,   0.0,  4,  insert_mem,   True,  insert_head_ref ],
  [ "insert_head_3x9_0.5_3", insert_head_msgs, 3,  9,   0.5,  3,  insert_mem,   True,  insert_head_ref ],
  [ "insert_tail_0x0_0.0_0", insert_tail_msgs, 0,  0,   0.0,  0,  insert_mem,   True,  insert_tail_ref ],
  [ "insert_tail_5x0_0.5_0", insert_tail_msgs, 5,  0,   0.5,  0,  insert_mem,   True,  insert_tail_ref ],
  [ "insert_tail_0x5_0.0_4", insert_tail_msgs, 0,  5,   0.0,  4,  insert_mem,   True,  insert_tail_ref ],
  [ "insert_tail_3x9_0.5_3", insert_tail_msgs, 3,  9,   0.5,  3,  insert_mem,   True,  insert_tail_ref ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_io_pipe_test( TestHarness( PolyDsuListInorderPipeline,
                                 test_params.msgs[::2],
                                 test_params.msgs[1::2],
                                 test_params.src,
                                 test_params.sink,
                                 test_params.stall,
                                 test_params.lat ),
                    test_params.mem,
                    test_params,
                    dump_vcd )
