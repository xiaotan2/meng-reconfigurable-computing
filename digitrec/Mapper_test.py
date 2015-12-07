#=========================================================================
# MapperPRTL_test
#=========================================================================

import pytest
import random

from pymtl        import *
from pclib.test   import TestVectorSimulator

from MapperPRTL   import MapperPRTL
from DistancePRTL import *


def test_mapper( test_verilog, dump_vcd ):

  a = random.randint(0,0x1ffffffffffff)
  b = random.randint(0,0x1ffffffffffff)
  c = Bits(49,a ^ b)
  d = Bits(49,0)
  for i in xrange(49):
    d += c[i:i+1]

  test_vectors = [
     # in0              in1              out
     [ 0x1ffffffffffff, 0x0000000000000, 0x31],
     [ a,               b,               d   ]
  ]

  model = MapperPRTL()
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]
  
  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()


