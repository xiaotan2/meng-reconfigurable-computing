#=========================================================================
# PolyDsuRbTreeO3Pipeline_test
#=========================================================================

import pytest
import struct

from pymtl             import *
from pclib.test        import TestSource, TestSink, mk_test_case_table

from PolyDsuRbTreeO3Pipeline import PolyDsuRbTreeO3Pipeline
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
    return s.src.done & s.sink.done & s.model.rbtree_xcel.rbtree_lsq.queue.ctrl.empty

  def line_trace( s ):
    return s.model.line_trace()

#-------------------------------------------------------------------------
# run_o3_pipe_test
#-------------------------------------------------------------------------
def run_o3_pipe_test( model, mem_array, test_params, dump_vcd = None ):

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

def dsu_req_wr( ds_id, opq, addr, data, valid ):
  return dsu_req( ds_id, opq, PolyDsuReqMsg.TYPE_SET, addr, data, valid )

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

def xcel_req( id_, opq, opc, raddr, rdata, valid=0 ):
  msg = PolyDsuReqMsg()
  msg.id  = id_
  msg.opq = opq
  msg.opc = opc

  msg[ PolyDsuReqMsg.raddr ] = raddr
  msg[ PolyDsuReqMsg.rdata ] = rdata
  msg[ PolyDsuReqMsg.iter_ ] = valid

  return msg

xcel_resp = PolyDsuRespMsg().mk_xcel_msg

MTX = PolyDsuReqMsg.TYPE_MTX
MFX = PolyDsuReqMsg.TYPE_MFX

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
  dsu_req_rd ( 0x400,  1,   24,    0 ), dsu_resp_rd ( 0x400,  1,  24,   2 ),
  dsu_req_rd ( 0x400,  2,   48,    0 ), dsu_resp_rd ( 0x400,  2,  48,   3 ),
  dsu_req_rd ( 0x400,  3,   72,    0 ), dsu_resp_rd ( 0x400,  3,  72,   1 ),
  dsu_req_rd ( 0x400,  4,   96,    0 ), dsu_resp_rd ( 0x400,  4,  96,   4 ),

  dsu_req_inc( 0x400,  5,   24,    0 ), dsu_resp_inc( 0x400,  5,  48,   0 ),
  dsu_req_inc( 0x400,  6,   48,    0 ), dsu_resp_inc( 0x400,  6,  96,   0 ),
  dsu_req_inc( 0x400,  7,   72,    0 ), dsu_resp_inc( 0x400,  7,  24,   0 ),
  dsu_req_inc( 0x400,  8,   96,    0 ), dsu_resp_inc( 0x400,  8,   0,   0 ),

  dsu_req_dec( 0x400,  9,   24,    0 ), dsu_resp_dec( 0x400,  9,  72,   0 ),
  dsu_req_dec( 0x400, 10,   48,    0 ), dsu_resp_dec( 0x400, 10,  24,   0 ),
  dsu_req_dec( 0x400, 11,   72,    0 ), dsu_resp_dec( 0x400, 11,   0,   0 ),
  dsu_req_dec( 0x400, 12,   96,    0 ), dsu_resp_dec( 0x400, 12,  48,   0 ),

  dsu_req_wr ( 0x400, 13,   24,  1,0 ), dsu_resp_wr ( 0x400, 13,  24,   0 ),
  dsu_req_wr ( 0x400, 14,   48,  2,0 ), dsu_resp_wr ( 0x400, 14,  48,   0 ),
  dsu_req_wr ( 0x400, 15,   72,  3,0 ), dsu_resp_wr ( 0x400, 15,  72,   0 ),
  dsu_req_wr ( 0x400, 16,   96,  4,0 ), dsu_resp_wr ( 0x400, 16,  96,   0 ),

  dsu_req_wr ( 0x400, 17,   24,  5,1 ), dsu_resp_wr ( 0x400, 17,  24,   0 ),
  dsu_req_wr ( 0x400, 18,   48,  6,1 ), dsu_resp_wr ( 0x400, 18,  48,   0 ),
  dsu_req_wr ( 0x400, 19,   72,  7,1 ), dsu_resp_wr ( 0x400, 19,  72,   0 ),
  dsu_req_wr ( 0x400, 20,   96,  8,1 ), dsu_resp_wr ( 0x400, 20,  96,   0 ),

  dsu_req_rd ( 0x400, 21,   24,    0 ), dsu_resp_rd ( 0x400, 21,  24,   5 ),
  dsu_req_rd ( 0x400, 22,   48,    0 ), dsu_resp_rd ( 0x400, 22,  48,   6 ),
  dsu_req_rd ( 0x400, 23,   72,    0 ), dsu_resp_rd ( 0x400, 23,  72,   7 ),
  dsu_req_rd ( 0x400, 24,   96,    0 ), dsu_resp_rd ( 0x400, 24,  96,   8 ),

  dsu_req_inc( 0x400, 25,   24,    0 ), dsu_resp_inc( 0x400, 25,  48,   0 ),
  dsu_req_inc( 0x400, 26,   48,    0 ), dsu_resp_inc( 0x400, 26,  96,   0 ),
  dsu_req_inc( 0x400, 27,   72,    0 ), dsu_resp_inc( 0x400, 27,  24,   0 ),
  dsu_req_inc( 0x400, 28,   96,    0 ), dsu_resp_inc( 0x400, 28,   0,   0 ),

  dsu_req_rd ( 0x400, 29,   24,    0 ), dsu_resp_rd ( 0x400, 29,  24,   5 ),
  dsu_req_rd ( 0x400, 30,   48,    0 ), dsu_resp_rd ( 0x400, 30,  48,   6 ),
  dsu_req_rd ( 0x400, 31,   72,    0 ), dsu_resp_rd ( 0x400, 31,  72,   7 ),
  dsu_req_rd ( 0x400, 32,   96,    0 ), dsu_resp_rd ( 0x400, 32,  96,   8 ),
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
  #               id opq  opc raddr rdata  commit                id  opq  opc  rdata
  xcel_req   ( 0x400,  0, MTX,   1,     0, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, MTX,   2,    96, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX,   3,     4, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  1, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   1, MFX,    96 ), # result = mem_pos
  dsu_req_wr ( 0x400,  2,       96,     4, 1 ), dsu_resp_wr ( 0x400,   2,  96,     0 ), # write m_value

  xcel_req   ( 0x400,  0, MTX,   1,     0, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, MTX,   2,    24, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX,   3,     2, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  3, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   3, MFX,    24 ), # result = mem_pos
  dsu_req_wr ( 0x400,  4,       24,     2, 1 ), dsu_resp_wr ( 0x400,   4,  24,     0 ), # write m_value

  xcel_req   ( 0x400,  0, MTX,   1,     0, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, MTX,   2,    48, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX,   3,     3, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  5, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   5, MFX,    48 ), # result = mem_pos
  dsu_req_wr ( 0x400,  6,       48,     3, 1 ), dsu_resp_wr ( 0x400,   6,  48,     0 ), # write m_value

  xcel_req   ( 0x400,  0, MTX,   1,     0, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # pos
  xcel_req   ( 0x400,  0, MTX,   2,    72, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # mem_pos
  xcel_req   ( 0x400,  0, MTX,   3,     1, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  7, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   7, MFX,    72 ), # result = mem_pos
  dsu_req_wr ( 0x400,  8,       72,     1, 1 ), dsu_resp_wr ( 0x400,   8,  72,     0 ), # write m_value

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
  run_o3_pipe_test( TestHarness( PolyDsuRbTreeO3Pipeline,
                                 test_params.msgs[::2],
                                 test_params.msgs[1::2],
                                 test_params.src,
                                 test_params.sink,
                                 test_params.stall,
                                 test_params.lat ),
                    test_params.mem,
                    test_params,
                    dump_vcd )
