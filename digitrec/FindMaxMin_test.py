#=========================================================================
# FindMaxMin_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import TestVectorSimulator

from FindMaxMin  import FindMax, FindMaxIdx, FindMin, FindMinIdx

#-----------------------------------------------------------------------
# FindMax 2 inpus unit test
#-----------------------------------------------------------------------

def test_FindMax_2( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   out
    [ 0x01, 0x02, 0x02 ],
    [ 0x05, 0x02, 0x05 ],
    [ 0x00, 0x04, 0x04 ],
    [ 0x02, 0x03, 0x03 ],
    [ 0x06, 0x06, 0x06 ],
    [ 0x07, 0x03, 0x07 ],
    [ 0x08, 0x08, 0x08 ],
    [ 0x00, 0x00, 0x00 ],
    [ 0x32, 0x32, 0x32 ],
    [ 0x30, 0x31, 0x31 ],
  ]

  model = FindMax( 6, 2 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# FindMax unit test
#-----------------------------------------------------------------------

def test_FindMax_3( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   out
    [ 0x01, 0x02, 0x03, 0x03 ],
    [ 0x05, 0x02, 0x03, 0x05 ],
    [ 0x00, 0x04, 0x03, 0x04 ],
    [ 0x02, 0x03, 0x03, 0x03 ],
    [ 0x06, 0x06, 0x05, 0x06 ],
    [ 0x07, 0x03, 0x07, 0x07 ],
    [ 0x08, 0x08, 0x08, 0x08 ],
    [ 0x00, 0x00, 0x00, 0x00 ],
    [ 0x32, 0x32, 0x32, 0x32 ],
    [ 0x30, 0x30, 0x31, 0x31 ],
  ]

  model = FindMax( 6, 3 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.out.value == test_vector[3]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()



#-----------------------------------------------------------------------
# FindMaxIdx unit test
#-----------------------------------------------------------------------

def test_FindMaxIdx_3( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   out   idx
    [ 0x01, 0x02, 0x03, 0x03, 0x2 ],
    [ 0x05, 0x02, 0x03, 0x05, 0x0 ],
    [ 0x00, 0x04, 0x03, 0x04, 0x1 ],
    [ 0x02, 0x03, 0x03, 0x03, 0x1 ],
    [ 0x06, 0x06, 0x05, 0x06, 0x0 ],
    [ 0x07, 0x03, 0x07, 0x07, 0x0 ],
    [ 0x08, 0x08, 0x08, 0x08, 0x0 ],
    [ 0x00, 0x00, 0x00, 0x00, 0x0 ],
    [ 0x32, 0x32, 0x32, 0x32, 0x0 ],
    [ 0x30, 0x30, 0x31, 0x31, 0x2 ],
  ]

  model = FindMaxIdx( 6, 3 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.out.value == test_vector[3]
    if test_vector[4] != '?':
      assert model.idx.value == test_vector[4]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()



#-----------------------------------------------------------------------
# FindMin unit test
#-----------------------------------------------------------------------

def test_FindMin_3( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   out
    [ 0x01, 0x02, 0x03, 0x01 ],
    [ 0x05, 0x02, 0x03, 0x02 ],
    [ 0x07, 0x04, 0x03, 0x03 ],
    [ 0x02, 0x02, 0x03, 0x02 ],
    [ 0x06, 0x05, 0x05, 0x05 ],
    [ 0x07, 0x0a, 0x07, 0x07 ],
    [ 0x08, 0x08, 0x08, 0x08 ],
    [ 0x00, 0x00, 0x00, 0x00 ],
    [ 0x32, 0x32, 0x32, 0x32 ],
    [ 0x32, 0x32, 0x03, 0x03 ],
  ]
 
  model = FindMin( 6, 3 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()
 
  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]
 
  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.out.value == test_vector[3]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-----------------------------------------------------------------------
# FindMinIdx unit test
#-----------------------------------------------------------------------

def test_FindMinIdx_3( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   out   idx
    [ 0x01, 0x02, 0x03, 0x01, 0x0 ],
    [ 0x05, 0x02, 0x03, 0x02, 0x1 ],
    [ 0x07, 0x04, 0x03, 0x03, 0x2 ],
    [ 0x02, 0x02, 0x03, 0x02, 0x0 ],
    [ 0x06, 0x05, 0x05, 0x05, 0x1 ],
    [ 0x07, 0x0a, 0x07, 0x07, 0x0 ],
    [ 0x08, 0x08, 0x08, 0x08, 0x0 ],
    [ 0x00, 0x00, 0x00, 0x00, 0x0 ],
    [ 0x32, 0x32, 0x32, 0x32, 0x0 ],
    [ 0x32, 0x32, 0x03, 0x03, 0x2 ],
  ]

  model = FindMinIdx( 6, 3 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]

  def tv_out( model, test_vector ):
    if test_vector[3] != '?':
      assert model.out.value == test_vector[3]
    if test_vector[4] != '?':
      assert model.idx.value == test_vector[4]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

 
