#=========================================================================
# PolyDsuBinTreeO3Pipeline_test
#=========================================================================

import pytest
import struct

from pymtl             import *
from pclib.test        import TestSource, TestSink, mk_test_case_table

from PolyDsuBinTreeO3Pipeline import PolyDsuBinTreeO3Pipeline
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
    return s.src.done & s.sink.done & s.model.bintree_xcel.bintree_lsq.queue.ctrl.empty

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
    assert result == test_params.ref

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
simple_mem = mem_array_int( 0,
    [
      0,    0,    0,    0,    #  0
      0,    64,   64,   0,    # 16 header
      64,   0,    48,   1,    # 32
      32,   0,    0,    2,    # 48
      16,   32,   96,   3,    # 64
      96,   0,    0,    4,    # 80
      64,   80,   112,  5,    # 96
      96,   0,    0,    6,    # 112
    ]
  )

bintree_int_msgs = [
  # bintree-iterator operations
  #               id opq  addr  data                     id opq addr data
  dsu_req_rd ( 0x400,  0,   16,    0 ), dsu_resp_rd ( 0x400,  0,  16,   0 ),
  dsu_req_rd ( 0x400,  0,   32,    0 ), dsu_resp_rd ( 0x400,  0,  32,   1 ),
  dsu_req_rd ( 0x400,  0,   48,    0 ), dsu_resp_rd ( 0x400,  0,  48,   2 ),
  dsu_req_rd ( 0x400,  0,   64,    0 ), dsu_resp_rd ( 0x400,  0,  64,   3 ),
  dsu_req_rd ( 0x400,  0,   80,    0 ), dsu_resp_rd ( 0x400,  0,  80,   4 ),
  dsu_req_rd ( 0x400,  0,   96,    0 ), dsu_resp_rd ( 0x400,  0,  96,   5 ),
  dsu_req_rd ( 0x400,  0,   112,   0 ), dsu_resp_rd ( 0x400,  0,  112,  6 ),

  dsu_req_inc( 0x400,  0,   32,    0 ), dsu_resp_inc( 0x400,  0,  48,   0 ),
  dsu_req_inc( 0x400,  0,   48,    0 ), dsu_resp_inc( 0x400,  0,  64,   0 ),
  dsu_req_inc( 0x400,  0,   64,    0 ), dsu_resp_inc( 0x400,  0,  80,   0 ),
  dsu_req_inc( 0x400,  0,   80,    0 ), dsu_resp_inc( 0x400,  0,  96,   0 ),
  dsu_req_inc( 0x400,  0,   96,    0 ), dsu_resp_inc( 0x400,  0,  112,  0 ),
  dsu_req_inc( 0x400,  0,   112,   0 ), dsu_resp_inc( 0x400,  0,  16,   0 ),

  dsu_req_dec( 0x400,  0,   16,    0 ), dsu_resp_dec( 0x400,  0,  112,  0 ),
  dsu_req_dec( 0x400,  0,   112,   0 ), dsu_resp_dec( 0x400,  0,  96,   0 ),
  dsu_req_dec( 0x400,  0,   96,    0 ), dsu_resp_dec( 0x400,  0,  80,   0 ),
  dsu_req_dec( 0x400,  0,   80,    0 ), dsu_resp_dec( 0x400,  0,  64,   0 ),
  dsu_req_dec( 0x400,  0,   64,    0 ), dsu_resp_dec( 0x400,  0,  48,   0 ),
  dsu_req_dec( 0x400,  0,   48,    0 ), dsu_resp_dec( 0x400,  0,  32,   0 ),

  dsu_req_wr ( 0x400,  1,   32,  5,0 ), dsu_resp_wr ( 0x400,  1,  32,   0 ),
  dsu_req_wr ( 0x400,  2,   48,  6,0 ), dsu_resp_wr ( 0x400,  2,  48,   0 ),
  dsu_req_wr ( 0x400,  3,   64,  7,0 ), dsu_resp_wr ( 0x400,  3,  64,   0 ),
  dsu_req_wr ( 0x400,  4,   80,  8,0 ), dsu_resp_wr ( 0x400,  4,  80,   0 ),
  
  dsu_req_wr ( 0x400,  1,   32,  5,1 ), dsu_resp_wr ( 0x400,  1,  32,   0 ),
  dsu_req_wr ( 0x400,  2,   48,  6,1 ), dsu_resp_wr ( 0x400,  2,  48,   0 ),
  dsu_req_wr ( 0x400,  3,   64,  7,1 ), dsu_resp_wr ( 0x400,  3,  64,   0 ),
  dsu_req_wr ( 0x400,  4,   80,  8,1 ), dsu_resp_wr ( 0x400,  4,  80,   0 ),

  dsu_req_rd ( 0x400,  0,   32,    0 ), dsu_resp_rd ( 0x400,  0,  32,   5 ),
  dsu_req_rd ( 0x400,  0,   48,    0 ), dsu_resp_rd ( 0x400,  0,  48,   6 ),
  dsu_req_rd ( 0x400,  0,   64,    0 ), dsu_resp_rd ( 0x400,  0,  64,   7 ),
  dsu_req_rd ( 0x400,  0,   80,    0 ), dsu_resp_rd ( 0x400,  0,  80,   8 ),

]

#---------------------------------------------------------------
# Test 2: insert
#---------------------------------------------------------------

insert_mem = mem_array_int( 0,
    [
      0,    0,    0,    0,    #  0
      0,    64,   64,   0,    # 16 header
      0,    0,    0,    0,    # 32
      0,    0,    0,    0,    # 48
      16,   0,    0,    3,    # 64 root
      0,    0,    0,    0,    # 80
      0,    0,    0,    0,    # 96
      0,    0,    0,    0,    # 112
    ]
  )

insert_ref = [
      0,    0,    0,    0,    #  0
      0,    64,   64,   0,    # 16 header
      64,   0,    48,   1,    # 32
      32,   0,    0,    2,    # 48
      16,   32,   96,   3,    # 64 root
      96,   0,    0,    4,    # 80
      64,   80,   112,  5,    # 96
      96,   0,    0,    6,    # 112
    ]

# simple tree
#     3
#   /   \
#  1     5
#   \   / \
#    2 4   6

insert_msgs = [
  # insert messages
  #               id opq  opc raddr rdata commit              id  opq  opc  rdata
  # 3->1
  xcel_req   ( 0x400,  0, MTX,   1,    64, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # header
  xcel_req   ( 0x400,  0, MTX,   2,    32, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # node mem
  xcel_req   ( 0x400,  0, MTX,   3,     1, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  1, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   1, MFX,    32 ), # result = mem

  # 3->5
  xcel_req   ( 0x400,  0, MTX,   1,    64, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # header
  xcel_req   ( 0x400,  0, MTX,   2,    96, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # node mem
  xcel_req   ( 0x400,  0, MTX,   3,     5, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  2, MFX,   1,     0, 1 ), xcel_resp   ( 0x400,   2, MFX,    96 ), # result = mem

  # 1->2
  xcel_req   ( 0x400,  0, MTX,   1,    32, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # header
  xcel_req   ( 0x400,  0, MTX,   2,    48, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # node mem
  xcel_req   ( 0x400,  0, MTX,   3,     2, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  3, MFX,   1,     0, 1 ), xcel_resp   ( 0x400,   3, MFX,    48 ), # result = mem

  # 5->4
  xcel_req   ( 0x400,  0, MTX,   1,    96, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # header
  xcel_req   ( 0x400,  0, MTX,   2,    80, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # node mem
  xcel_req   ( 0x400,  0, MTX,   3,     4, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  4, MFX,   0,     0, 1 ), xcel_resp   ( 0x400,   4, MFX,    80 ), # result = mem

  # 5->6
  xcel_req   ( 0x400,  0, MTX,   1,    96, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # header
  xcel_req   ( 0x400,  0, MTX,   2,   112, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # node mem
  xcel_req   ( 0x400,  0, MTX,   3,     6, 0 ), xcel_resp   ( 0x400,   0, MTX,     0 ), # val
  xcel_req   ( 0x400,  5, MFX,   1,     0, 1 ), xcel_resp   ( 0x400,   5, MFX,   112 ), # result = mem

]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                            "msgs              src sink  stall lat   mem        insert  ref" ),
  [ "bintree_int_0x0_0.0_0",    bintree_int_msgs,   0,  0,   0.0,  0,  simple_mem,  False, None ],
  [ "bintree_int_5x0_0.5_0",    bintree_int_msgs,   5,  0,   0.5,  0,  simple_mem,  False, None ],
  [ "bintree_int_0x5_0.0_4",    bintree_int_msgs,   0,  5,   0.0,  4,  simple_mem,  False, None ],
  [ "bintree_int_3x9_0.5_3",    bintree_int_msgs,   3,  9,   0.5,  3,  simple_mem,  False, None ],
  [ "insert_0x0_0.0_0",         insert_msgs,        0,  0,   0.0,  0,  insert_mem,  True,  insert_ref ],
  [ "insert_5x0_0.5_0",         insert_msgs,        5,  0,   0.5,  0,  insert_mem,  True,  insert_ref ],
  [ "insert_0x5_0.0_4",         insert_msgs,        0,  5,   0.0,  4,  insert_mem,  True,  insert_ref ],
  [ "insert_3x9_0.5_3",         insert_msgs,        3,  9,   0.5,  3,  insert_mem,  True,  insert_ref ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_o3_pipe_test( TestHarness( PolyDsuBinTreeO3Pipeline,
                                 test_params.msgs[::2],
                                 test_params.msgs[1::2],
                                 test_params.src,
                                 test_params.sink,
                                 test_params.stall,
                                 test_params.lat ),
                    test_params.mem,
                    test_params,
                    dump_vcd )
