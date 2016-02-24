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
     ( 'in0', 'in1', 'in2', 'in3', 'out' ),
     [  0x01,  0x02,  0x03,  0x04,  0x0e ],
   ], dump_vcd )

