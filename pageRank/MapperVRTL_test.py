#=========================================================================
# MapperVRTL_test
#=========================================================================

import pytest
import random

from pymtl            import *
from pclib.test       import run_test_vector_sim

from MapperVRTL       import *

#-----------------------------------------------------------------------
# MapperVRTL unit test
#-----------------------------------------------------------------------

def test_small( dump_vcd ):
  run_test_vector_sim( MapperVRTL(), [
     ( 'r_0', 'g_0', 'r_1', 'g_1', 'out' ),
     [  0x01,  0x02,  0x03,  0x04,  0x00 ],
     [  0x03,  0x02,  0x03,  0x04,  0x0e ],
   ], dump_vcd )


# Random test

def test_random( dump_vcd ):

  test_vector_table = [( 'r_0', 'g_0', 'r_1', 'g_1', 'out*' )]

  # first cycle outputs
  out = Bits( 32, 0x0 )

  for i in xrange( 100 ):
    r_0    = Bits( 32, random.randint(0, 0xffffffff) )
    g_0    = Bits( 32, random.randint(0, 0xffffffff) )
    r_1    = Bits( 32, random.randint(0, 0xffffffff) )
    g_1    = Bits( 32, random.randint(0, 0xffffffff) )

    test_vector_table.append( [ r_0, g_0, r_1, g_1, out ] )

    out    = Bits( 32, r_0 * g_0 + r_1 * g_1, trunc=True )

  run_test_vector_sim( MapperVRTL(), test_vector_table, dump_vcd )

