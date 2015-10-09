#=========================================================================
# PolyDsuRbTreeInorderPipeline_tests
#=========================================================================

import pytest
import struct

from pymtl             import *
from pclib.test        import TestSource, TestSink, mk_test_case_table

from PolyDsuRbTreeInorderPipeline import PolyDsuRbTreeInorderPipeline

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

TYPE_MTX = PolyDsuReqMsg.TYPE_MTX
TYPE_MFX = PolyDsuReqMsg.TYPE_MFX

#-------------------------------------------------------------------------
# Test 1: incr, decr, get, set
#-------------------------------------------------------------------------

# preload the memory to known values
# 72 -> 24 -> 48 -> 96
rbtree_int_mem = mem_array_int( 0,
    [
      24,   72,   96,   0,  255,  255,    #  0, header
      0,    72,   48,   1,    2,    2,    # 24
      24,   0,    96,   1,    3,    3,    # 48
      24,   0,     0,   1,    1,    1,    # 72
      48,   0,     0,   0,    4,    4,    # 96
    ]
  )

rbtree_int_msgs = [
  # rbtree-iterator operations
  #               id opq  addr  data                     id opq addr data
  dsu_req_rd ( 0x400,  0,   24,    0 ), dsu_resp_rd ( 0x400,  0,  24,   2 ),
  dsu_req_rd ( 0x400,  0,   48,    0 ), dsu_resp_rd ( 0x400,  0,  48,   3 ),
  dsu_req_rd ( 0x400,  0,   72,    0 ), dsu_resp_rd ( 0x400,  0,  72,   1 ),
  dsu_req_rd ( 0x400,  0,   96,    0 ), dsu_resp_rd ( 0x400,  0,  96,   4 ),

  dsu_req_inc( 0x400,  0,   24,    0 ), dsu_resp_inc( 0x400,  0,  48,   0 ),
  dsu_req_inc( 0x400,  0,   48,    0 ), dsu_resp_inc( 0x400,  0,  96,   0 ),
  dsu_req_inc( 0x400,  0,   72,    0 ), dsu_resp_inc( 0x400,  0,  24,   0 ),
  dsu_req_inc( 0x400,  0,   96,    0 ), dsu_resp_inc( 0x400,  0,   0,   0 ),

  dsu_req_dec( 0x400,  0,   24,    0 ), dsu_resp_dec( 0x400,  0,  72,   0 ),
  dsu_req_dec( 0x400,  0,   48,    0 ), dsu_resp_dec( 0x400,  0,  24,   0 ),
  dsu_req_dec( 0x400,  0,   72,    0 ), dsu_resp_dec( 0x400,  0,   0,   0 ),
  dsu_req_dec( 0x400,  0,   96,    0 ), dsu_resp_dec( 0x400,  0,  48,   0 ),

  dsu_req_wr ( 0x400,  0,   24,    5 ), dsu_resp_wr ( 0x400,  0,  24,   0 ),
  dsu_req_wr ( 0x400,  0,   48,    6 ), dsu_resp_wr ( 0x400,  0,  48,   0 ),
  dsu_req_wr ( 0x400,  0,   72,    7 ), dsu_resp_wr ( 0x400,  0,  72,   0 ),
  dsu_req_wr ( 0x400,  0,   96,    8 ), dsu_resp_wr ( 0x400,  0,  96,   0 ),

  dsu_req_rd ( 0x400,  0,   24,    0 ), dsu_resp_rd ( 0x400,  0,  24,   5 ),
  dsu_req_rd ( 0x400,  0,   48,    0 ), dsu_resp_rd ( 0x400,  0,  48,   6 ),
  dsu_req_rd ( 0x400,  0,   72,    0 ), dsu_resp_rd ( 0x400,  0,  72,   7 ),
  dsu_req_rd ( 0x400,  0,   96,    0 ), dsu_resp_rd ( 0x400,  0,  96,   8 ),

]

#---------------------------------------------------------------
# Test 2: insert
#---------------------------------------------------------------

insert_mem = mem_array_int( 0,
  [
    0,    0,    0,    0,    255,  255,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  ]
)

insert_ref = [
    48,   72,   96,   0,  255,  255,    #  0, header
    48,   72,    0,   1,    2,    2,    # 24
     0,   24,   96,   1,    3,    3,    # 48
    24,    0,    0,   0,    1,    1,    # 72
    48,    0,    0,   1,    4,    4,    # 96
  ]

insert_msgs = [
  # insert messages
  #               id opq       opc raddr rdata                     id  opq       opc  rdata
  xcel_req   ( 0x400,  0, TYPE_MTX,   1,     0 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   2,    96 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   3,     4 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # val
  xcel_req   ( 0x400,  0, TYPE_MFX,   0,     0 ), xcel_resp   ( 0x400,   0, TYPE_MFX,    96 ), # result = mem_pos
  dsu_req_wr ( 0x400,  0,            96,     4 ), dsu_resp_wr ( 0x400,   0,       96,     0 ), # write m_value

  xcel_req   ( 0x400,  0, TYPE_MTX,   1,     0 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   2,    24 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   3,     2 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # val
  xcel_req   ( 0x400,  0, TYPE_MFX,   0,     0 ), xcel_resp   ( 0x400,   0, TYPE_MFX,    24 ), # result = mem_pos
  dsu_req_wr ( 0x400,  0,            24,     2 ), dsu_resp_wr ( 0x400,   0,       24,     0 ), # write m_value

  xcel_req   ( 0x400,  0, TYPE_MTX,   1,     0 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   2,    48 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   3,     3 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # val
  xcel_req   ( 0x400,  0, TYPE_MFX,   0,     0 ), xcel_resp   ( 0x400,   0, TYPE_MFX,    48 ), # result = mem_pos
  dsu_req_wr ( 0x400,  0,            48,     3 ), dsu_resp_wr ( 0x400,   0,       48,     0 ), # write m_value

  xcel_req   ( 0x400,  0, TYPE_MTX,   1,     0 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   2,    72 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, TYPE_MTX,   3,     1 ), xcel_resp   ( 0x400,   0, TYPE_MTX,     0 ), # val
  xcel_req   ( 0x400,  0, TYPE_MFX,   0,     0 ), xcel_resp   ( 0x400,   0, TYPE_MFX,    72 ), # result = mem_pos
  dsu_req_wr ( 0x400,  0,            72,     1 ), dsu_resp_wr ( 0x400,   0,       72,     0 ), # write m_value

]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                          "msgs             src sink stall lat mem           insert ref_data"       ),
  [ "rbtree_int_0x0_0.0_0",    rbtree_int_msgs,    0,  0,   0.0,  0,  rbtree_int_mem, False, None       ],
  [ "rbtree_int_5x0_0.5_0",    rbtree_int_msgs,    5,  0,   0.5,  0,  rbtree_int_mem, False, None       ],
  [ "rbtree_int_0x5_0.0_4",    rbtree_int_msgs,    0,  5,   0.0,  4,  rbtree_int_mem, False, None       ],
  [ "rbtree_int_3x9_0.5_3",    rbtree_int_msgs,    3,  9,   0.5,  3,  rbtree_int_mem, False, None       ],
  [ "insert_0x0_0.0_0",        insert_msgs,        0,  0,   0.0,  0,  insert_mem,     True,  insert_ref ],
  [ "insert_5x0_0.5_0",        insert_msgs,        5,  0,   0.5,  0,  insert_mem,     True,  insert_ref ],
  [ "insert_0x5_0.0_4",        insert_msgs,        0,  5,   0.0,  4,  insert_mem,     True,  insert_ref ],
  [ "insert_3x9_0.5_3",        insert_msgs,        3,  9,   0.5,  3,  insert_mem,     True,  insert_ref ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_io_pipe_test( TestHarness( PolyDsuRbTreeInorderPipeline,
                         test_params.msgs[::2],
                         test_params.msgs[1::2],
                         test_params.src,
                         test_params.sink,
                         test_params.stall,
                         test_params.lat ),
            test_params.mem,
            test_params,
            dump_vcd )
