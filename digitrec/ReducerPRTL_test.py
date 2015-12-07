#=========================================================================
# ReducerPRTL_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import TestVectorSimulator

from ReducerPRTL  import *

#-----------------------------------------------------------------------
# Reducer unit test
#-----------------------------------------------------------------------

def test_ReducerPRTL( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   rst  out
    [ 0x00, 0x00, 0x00, 0x1, 0x96 ],
    [ 0x32, 0x31, 0x30, 0x0, 0x96 ],
    [ 0x29, 0x28, 0x29, 0x0, 0x94 ],
    [ 0x27, 0x29, 0x28, 0x0, 0x8a ],
    [ 0x25, 0x23, 0x24, 0x0, 0x7f ],
    [ 0x30, 0x29, 0x32, 0x0, 0x72 ],
    [ 0x07, 0x03, 0x03, 0x0, 0x72 ],
    [ 0x28, 0x26, 0x25, 0x0, 0x4d ],
    [ 0x00, 0x00, 0x00, 0x0, 0x4b ],
    [ 0x32, 0x32, 0x32, 0x0, 0x26 ],
    [ 0x30, 0x31, 0x31, 0x0, 0x26 ],
    [ 0x30, 0x31, 0x31, 0x1, 0x26 ],
    [ 0x02, 0x01, 0x05, 0x0, 0x96 ],
    [ 0x30, 0x01, 0x17, 0x0, 0x65 ],
    [ 0x30, 0x01, 0x17, 0x0, 0x34 ],
  ]

  model = ReducerPRTL( 3, 6, 3, 50 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_[0].value = test_vector[0]
    model.in_[1].value = test_vector[1]
    model.in_[2].value = test_vector[2]
    model.rst.value    = test_vector[3]

  def tv_out( model, test_vector ):
    if test_vector[4] != '?':
      assert model.out.value == test_vector[4]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

