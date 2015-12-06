#=========================================================================
# AdderTree_test
#=========================================================================

import pytest
import random

from pymtl       import *
from pclib.test  import TestVectorSimulator

from AdderTree   import *


def test_AdderTree( test_verilog, dump_vcd ):

  test_vectors = [
    # in0   in1   in2   out
    [ 0x01, 0x02, 0x02, 0x05 ],
    [ 0x05, 0x02, 0x05, 0x0c ],
    [ 0x00, 0x04, 0x04, 0x08 ],
    [ 0x02, 0x03, 0x03, 0x08 ],
    [ 0x06, 0x06, 0x06, 0x12 ],
    [ 0x07, 0x03, 0x07, 0x11 ],
    [ 0x08, 0x08, 0x08, 0x18 ],
    [ 0x00, 0x00, 0x00, 0x00 ],
    [ 0x32, 0x32, 0x32, 0x60 ],
    [ 0x30, 0x31, 0x31, 0x5c ],
  ]

  model = AdderTree( 6, 3 )
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


 
