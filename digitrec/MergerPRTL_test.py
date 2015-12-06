#=========================================================================
# MergerPRTL_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import TestVectorSimulator
from MergerPRTL  import *

#-----------------------------------------------------------------------
# Merger unit test
#-----------------------------------------------------------------------

def test_MergerPRTL( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   in3   in4   in5   in6   in7   in8   in9   idx
    [ 0x96, 0x42, 0x03, 0x23, 0x89, 0x55, 0x78, 0x06, 0x09, 0x32, 0x2 ],
    [ 0x05, 0x77, 0x32, 0x96, 0x45, 0x23, 0x89, 0x09, 0x09, 0x01, 0x9 ],
    [ 0x00, 0x00, 0x03, 0x23, 0x89, 0x35, 0x43, 0x06, 0x09, 0x32, 0x0 ],
  ]

#  random.seed(0xdeadbeef)
#  test_vectors = []
#  for k in xrange( 50 ):
#    inputs = []
#    min_value = 0x96
#    min_idx   = 0
#    for i in xrange( 10 ):
#      input_value = random.randint( 0, 0x96 )
#      if ( input_value < min_value ):
#        min_value = input_value
#        min_idx   = i
#      inputs.append( input_value )
#    inputs.append( min_idx )
#    test_vectors.extend( inputs )

  model = MergerPRTL( 10, 8 )
  model.vcd_file = dump_vcd
  if test_verilog:
     model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    for i in xrange( 10 ):
      model.in_[i].value = test_vector[i]

  def tv_out( model, test_vector ):
    if test_vector[10] != '?':
      assert model.out.value == test_vector[10]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

