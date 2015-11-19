#=========================================================================
# Adder Test
#=========================================================================



from pymtl      import *
from pclib.test import TestVectorSimulator
from Adder      import Adder

#-------------------------------------------------------------------------
# test_4
#-------------------------------------------------------------------------

def test_adder( test_verilog ):

  # Test vectors

  test_vectors = [
    # in0     in1      out   
    [ 0x0001, 0x0010,  0x0011],
  ]

  # Instantiate and elaborate the model

  model = Adder()
  if test_verilog:
    model = TranslationTool( model )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in0.value = test_vector[0]
    model.in1.value = test_vector[1]

  def tv_out( model, test_vector ):
    if test_vector[2] != '?':
      assert model.out.value == test_vector[2]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
