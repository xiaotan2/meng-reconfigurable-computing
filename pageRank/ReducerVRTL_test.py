#=========================================================================
# ReducerVRTL_test
#=========================================================================

import pytest
import random

from pymtl            import *
from pclib.test       import run_test_vector_sim

from ReducerVRTL       import *

#-----------------------------------------------------------------------
# MapperVRTL unit test
#-----------------------------------------------------------------------

def test_small( dump_vcd ):
  run_test_vector_sim( ReducerVRTL(), [
     ( 'in0', 'in1', 'in2', 'in3', 'out' ),
     [  0x01,  0x02,  0x03,  0x04,  0x0e ],
     [  0x03,  0x02,  0x03,  0x04,  0x11 ],
   ], dump_vcd )


# Random test

def test_random( dump_vcd ):

  test_vector_table = [( 'in0', 'in1', 'in2', 'in3', 'out*' )]

  for i in xrange( 100 ):
    in0    = Bits( 32, random.randint(0, 0xffffffff) )
    in1    = Bits( 32, random.randint(0, 0xffffffff) )
    in2    = Bits( 32, random.randint(0, 0xffffffff) )
    in3    = Bits( 32, random.randint(0, 0xffffffff) )
    out    = Bits( 32, in0 + in1 + in2 + in3, trunc=True )

    test_vector_table.append( [ in0, in1, in2, in3, out ] )

                                                                                                                                                     
  run_test_vector_sim( ReducerVRTL(), test_vector_table, dump_vcd )

