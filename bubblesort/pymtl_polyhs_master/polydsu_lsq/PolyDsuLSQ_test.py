#==============================================================================
# PolyDsuLSQ_test.py
#==============================================================================

import pytest
import struct

from pymtl      import *
from pclib.test import TestSource, TestSink, TestVectorSimulator

from PolyDsuLSQ import PolyDsuLSQ
from CommitMsg  import CommitReqMsg

from xmem.MemMsgFuture     import MemMsg
from xmem.TestMemoryOpaque import TestMemory

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, num_entries, test_verilog=False ):

    # Interfaces
    mem_ifc = MemMsg(8,32,32)

    # Instantiate Models
    if test_verilog:
      s.lsq = TranslationTool( PolyDsuLSQ( num_entries ) )
    else:
      s.lsq = PolyDsuLSQ( num_entries )

    s.mem = TestMemory ( mem_ifc, 1, 0, 0 )

    # Connections
    s.connect( s.lsq.memreq_out,  s.mem.reqs[0]  )
    s.connect( s.lsq.memresp_out, s.mem.resps[0] )

#-------------------------------------------------------------------------
# test stores
#-------------------------------------------------------------------------

def test_stores( dump_vcd, test_verilog ):
  ''' White box tests that fills up the LSQ with store requests and then
      drains the LSQ based on the commit requests'''

  mreq  = MemMsg(8,32,32).req.mk_msg
  mresp = MemMsg(8,32,32).resp.mk_msg

  creq  = CommitReqMsg().mk_msg

  test_vectors = [
    # Enqueue                                                       Commit
    # mreq mreq mreq                 mresp mresp mresp              creq creq creq              cresp cresp
    # ival irdy imsg                 ival  irdy  msg                val  rdy  msg               val   rdy
    #
    [ 1,   1,   mreq(1,0x11, 0,0,1), 0,    1,    '?'              , 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x22, 4,0,2), 1,    1,    mresp(1,0x11,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x33, 8,0,3), 1,    1,    mresp(1,0x22,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x44,12,0,4), 1,    1,    mresp(1,0x33,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(1,0x44,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 1,   1,   creq(0,0,1,0x11), 0,    1 ],
    [ 1,   1,   mreq(1,0x55,16,0,5), 0,    0,    0,                 1,   1,   creq(0,0,0,0x22), 1,    1 ],
    [ 1,   1,   mreq(1,0x66,20,0,6), 1,    1,    mresp(1,0x55,0,0), 1,   1,   creq(0,0,0,0x33), 1,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(1,0x66,0,0), 1,   1,   creq(0,0,1,0x44), 1,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 1,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 1,   1,   creq(0,0,1,0x55), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 1,   1,   creq(0,0,1,0x66), 1,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 1,    1 ],
  ]

  # Instantiate and elaborate the model
  model          = TestHarness( 4, test_verilog )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in the model
  def tv_in( model, test_vector ):
    model.lsq.memreq_in.val.value  = test_vector[0]
    model.lsq.memreq_in.msg.value  = test_vector[2]
    model.lsq.memresp_in.rdy.value = test_vector[4]
    model.lsq.commitreq.val.value  = test_vector[6]
    model.lsq.commitreq.msg.value  = test_vector[8]
    model.lsq.commitresp.rdy.value = test_vector[10]

  def tv_out( model, test_vector ):

    assert model.lsq.memreq_in.rdy  == test_vector[1]
    assert model.lsq.memresp_in.val == test_vector[3]

    if test_vector[5] != '?' and model.lsq.memresp_in.val:
      assert model.lsq.memresp_in.msg == test_vector[5]

    assert model.lsq.commitreq.rdy  == test_vector[7]
    assert model.lsq.commitresp.val == test_vector[9]

  # Run the test
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

  # Retrieve data from test memory
  mem_bytes = model.mem.read_mem( 0, 24 )

  # Convert mem bytes into list of ints
  result_mem = list(struct.unpack("<{}I".format(6),buffer(mem_bytes)))

  # Expected values in memory
  ref_mem    = [1,0,0,4,5,6]

  # Compare result to reference
  assert ref_mem == result_mem

#-------------------------------------------------------------------------
# test non-overlapping loads and stores
#-------------------------------------------------------------------------

def test_non_overlapping_loads_stores( dump_vcd, test_verilog ):
  ''' White box test that buffers stores and handles non-overlapping loads
      that do not require store to load forwarding. NOTE: The test-vectors
      work for a round-robin based arbiter that does not necessarily
      priotorize loads over stores. Will need to change the tests if I
      replace the arbiter model '''

  mreq  = MemMsg(8,32,32).req.mk_msg
  mresp = MemMsg(8,32,32).resp.mk_msg

  creq  = CommitReqMsg().mk_msg

  test_vectors = [
    # Enqueue                                                       Commit
    # mreq mreq mreq                 mresp mresp mresp              creq creq creq              cresp cresp
    # ival irdy imsg                 ival  irdy  msg                val  rdy  msg               val   rdy
    #
    [ 1,   1,   mreq(1,0x11, 0,0,1), 0,    1,    '?'              , 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x22, 4,0,2), 1,    1,    mresp(1,0x11,0,0), 1,   1,   creq(0,0,1,0x11), 0,    1 ],
    [ 1,   1,   mreq(1,0x33, 8,0,3), 1,    1,    mresp(1,0x22,0,0), 1,   1,   creq(0,0,1,0x22), 1,    1 ],
    [ 1,   1,   mreq(0,0x55,16,0,0), 1,    1,    mresp(1,0x33,0,0), 1,   0,   creq(0,0,1,0x33), 1,    1 ],
    [ 1,   1,   mreq(1,0x44,12,0,4), 1,    1,    mresp(0,0x55,0,5), 1,   1,   creq(0,0,1,0x33), 0,    1 ],
    [ 1,   1,   mreq(0,0x66,20,0,0), 1,    1,    mresp(1,0x44,0,0), 1,   1,   creq(0,0,0,0x44), 1,    1 ],
    [ 1,   1,   mreq(0,0x77,24,0,0), 1,    1,    mresp(0,0x66,0,6), 0,   0,   creq(0,0,0,0   ), 1,    1 ],
    [ 1,   1,   mreq(0,0x88,28,0,0), 1,    1,    mresp(0,0x77,0,7), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(0,0x88,0,8), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
  ]

  # Instantiate and elaborate the model
  model          = TestHarness( 4, test_verilog )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Initialize test memory to known values
  data = [0,0,0,0,5,6,7,8]
  data_bytes = struct.pack("<{}I".format(len(data)),*data)
  model.mem.write_mem( 0, data_bytes )

  # Define functions mapping the test vector to ports in the model
  def tv_in( model, test_vector ):
    model.lsq.memreq_in.val.value  = test_vector[0]
    model.lsq.memreq_in.msg.value  = test_vector[2]
    model.lsq.memresp_in.rdy.value = test_vector[4]
    model.lsq.commitreq.val.value  = test_vector[6]
    model.lsq.commitreq.msg.value  = test_vector[8]
    model.lsq.commitresp.rdy.value = test_vector[10]

  def tv_out( model, test_vector ):

    assert model.lsq.memreq_in.rdy  == test_vector[1]
    assert model.lsq.memresp_in.val == test_vector[3]

    if test_vector[5] != '?' and model.lsq.memresp_in.val:
      assert model.lsq.memresp_in.msg == test_vector[5]

    assert model.lsq.commitreq.rdy  == test_vector[7]
    assert model.lsq.commitresp.val == test_vector[9]

  # Run the test
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

  # Retrieve data from test memory
  mem_bytes = model.mem.read_mem( 0, 32 )

  # Convert mem bytes into list of ints
  result_mem = list(struct.unpack("<{}I".format(8),buffer(mem_bytes)))

  # Expected values in memory
  ref_mem    = [1,2,3,0,5,6,7,8]

  # Compare result to reference
  assert ref_mem == result_mem

#-------------------------------------------------------------------------
# test store-load forwarding
#-------------------------------------------------------------------------

def test_store_load_forwarding( dump_vcd, test_verilog ):
  ''' White box test that buffers stores and handles multiple load requests
      that should bypass from the store queue '''

  mreq  = MemMsg(8,32,32).req.mk_msg
  mresp = MemMsg(8,32,32).resp.mk_msg

  creq  = CommitReqMsg().mk_msg

  test_vectors = [
    # Enqueue                                                       Commit
    # mreq mreq mreq                 mresp mresp mresp              creq creq creq              cresp cresp
    # ival irdy imsg                 ival  irdy  msg                val  rdy  msg               val   rdy
    #
    [ 1,   1,   mreq(0,0x01, 0,0,0), 0,    0,    0,                 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(0,0x02, 4,0,0), 1,    1,    mresp(0,0x01,0,1), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(0,0x03, 8,0,0), 1,    1,    mresp(0,0x02,0,2), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(0,0x04,12,0,0), 1,    1,    mresp(0,0x03,0,3), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(1,0x05, 0,0,5), 1,    1,    mresp(0,0x04,0,4), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(1,0x06, 0,0,6), 1,    1,    mresp(1,0x05,0,0), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(0,0x07, 0,0,0), 1,    1,    mresp(1,0x06,0,0), 1,   1,   creq(0,0,1,0x05), 0,    0 ],
    [ 1,   1,   mreq(0,0x08, 0,0,0), 1,    1,    mresp(0,0x07,0,6), 0,   0,   0,                1,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(0,0x08,0,6), 1,   1,   creq(0,0,0,0x06), 0,    1 ],
    [ 1,   1,   mreq(1,0x09, 4,0,6), 0,    1,    0,                 0,   0,   0,                1,    1 ],
    [ 1,   1,   mreq(1,0x11, 8,0,7), 1,    1,    mresp(1,0x09,0,0), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(1,0x12,12,0,8), 1,    1,    mresp(1,0x11,0,0), 0,   0,   0,                0,    0 ],
    [ 1,   1,   mreq(0,0x13,12,0,0), 1,    1,    mresp(1,0x12,0,0), 1,   1,   creq(0,0,1,0x09), 0,    0 ],
    [ 1,   1,   mreq(0,0x14, 4,0,0), 1,    1,    mresp(0,0x13,0,8), 0,   0,   0,                1,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(0,0x14,0,6), 1,   1,   creq(0,0,1,0x11), 0,    0 ],
    [ 1,   1,   mreq(0,0x15, 8,0,0), 0,    1,    0,                 0,   0,   0,                1,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(0,0x15,0,7), 1,   1,   creq(0,0,1,0x12), 0,    0 ],
    [ 0,   0,   0,                   0,    1,    0,                 0,   0,   0,                1,    1 ],
  ]

  # Instantiate and elaborate the model
  model          = TestHarness( 4, test_verilog )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Initialize test memory to known values
  data = [1,2,3,4]
  data_bytes = struct.pack("<{}I".format(len(data)),*data)
  model.mem.write_mem( 0, data_bytes )

  # Define functions mapping the test vector to ports in the model
  def tv_in( model, test_vector ):
    model.lsq.memreq_in.val.value  = test_vector[0]
    model.lsq.memreq_in.msg.value  = test_vector[2]
    model.lsq.memresp_in.rdy.value = test_vector[4]
    model.lsq.commitreq.val.value  = test_vector[6]
    model.lsq.commitreq.msg.value  = test_vector[8]
    model.lsq.commitresp.rdy.value = test_vector[10]

  def tv_out( model, test_vector ):

    assert model.lsq.memreq_in.rdy  == test_vector[1]
    assert model.lsq.memresp_in.val == test_vector[3]

    if test_vector[5] != '?' and model.lsq.memresp_in.val:
      assert model.lsq.memresp_in.msg == test_vector[5]

    assert model.lsq.commitreq.rdy  == test_vector[7]
    assert model.lsq.commitresp.val == test_vector[9]

  # Run the test
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

  # Retrieve data from test memory
  mem_bytes = model.mem.read_mem( 0, 16 )

  # Convert mem bytes into list of ints
  result_mem = list(struct.unpack("<{}I".format(4),buffer(mem_bytes)))

  # Expected values in memory
  ref_mem = [5,6,7,8]

  # Compare result to reference
  assert ref_mem == result_mem

#-------------------------------------------------------------------------
# test multiple stores
#-------------------------------------------------------------------------

def test_multiple_stores( dump_vcd, test_verilog ):
  ''' White box tests that fills up the LSQ with store requests and then
      drains the LSQ based on the commit requests. The test checks for
      multiple store squashing'''

  mreq  = MemMsg(8,32,32).req.mk_msg
  mresp = MemMsg(8,32,32).resp.mk_msg

  creq  = CommitReqMsg().mk_msg

  test_vectors = [
    # Enqueue                                                       Commit
    # mreq mreq mreq                 mresp mresp mresp              creq creq creq              cresp cresp
    # ival irdy imsg                 ival  irdy  msg                val  rdy  msg               val   rdy
    #
    [ 1,   1,   mreq(1,0x11, 0,0,1), 0,    1,    '?'              , 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x11, 4,0,2), 1,    1,    mresp(1,0x11,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x11, 8,0,3), 1,    1,    mresp(1,0x11,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x11,12,0,4), 1,    1,    mresp(1,0x11,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(1,0x11,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 1,   1,   creq(0,0,1,0x11), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x22, 0,0,5), 0,    1,    '?'              , 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 1,   1,   mreq(1,0x22, 4,0,6), 1,    1,    mresp(1,0x22,0,0), 0,   0,   creq(0,0,0,0   ), 1,    1 ],
    [ 1,   1,   mreq(1,0x22, 8,0,7), 1,    1,    mresp(1,0x22,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   1,    1,    mresp(1,0x22,0,0), 0,   0,   creq(0,0,0,0   ), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 1,   1,   creq(0,0,0,0x22), 0,    1 ],
    [ 0,   0,   0,                   0,    0,    0,                 0,   0,   creq(0,0,1,0x22), 1,    1 ],
  ]

  # Instantiate and elaborate the model
  model          = TestHarness( 4, test_verilog )
  model.vcd_file = dump_vcd
  model.elaborate()

  # Define functions mapping the test vector to ports in the model
  def tv_in( model, test_vector ):
    model.lsq.memreq_in.val.value  = test_vector[0]
    model.lsq.memreq_in.msg.value  = test_vector[2]
    model.lsq.memresp_in.rdy.value = test_vector[4]
    model.lsq.commitreq.val.value  = test_vector[6]
    model.lsq.commitreq.msg.value  = test_vector[8]
    model.lsq.commitresp.rdy.value = test_vector[10]

  def tv_out( model, test_vector ):

    assert model.lsq.memreq_in.rdy  == test_vector[1]
    assert model.lsq.memresp_in.val == test_vector[3]

    if test_vector[5] != '?' and model.lsq.memresp_in.val:
      assert model.lsq.memresp_in.msg == test_vector[5]

    assert model.lsq.commitreq.rdy  == test_vector[7]
    assert model.lsq.commitresp.val == test_vector[9]

  # Run the test
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

  # Retrieve data from test memory
  mem_bytes = model.mem.read_mem( 0, 16 )

  # Convert mem bytes into list of ints
  result_mem = list(struct.unpack("<{}I".format(4),buffer(mem_bytes)))

  # Expected values in memory
  ref_mem    = [1,2,3,4]

  # Compare result to reference
  assert ref_mem == result_mem
