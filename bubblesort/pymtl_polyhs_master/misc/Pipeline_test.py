#=========================================================================
# Pipeline_test.py
#=========================================================================
# Tests an inelastic pipeline with val-rdy interfaces.

import pytest
import random

from pymtl      import *

from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from Pipeline   import Pipeline

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, msgs, nstages, src_delay, sink_delay ):

    # Instantiate models

    s.src   = TestSource  ( 16, msgs,  src_delay  )
    s.model = Pipeline    ( 16, 4 )
    s.sink  = TestSink    ( 16, msgs, sink_delay )

    # Connect

    s.connect( s.src.out,   s.model.in_ )
    s.connect( s.model.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " > " + \
           s.model.line_trace() + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# Test src/sink messages
#-------------------------------------------------------------------------

random.seed(0xdeadbeef)

basic_msgs  = [ 0, 1, 2, 3, 4 ]
random_msgs = [ random.randint(0,0xffff) for _ in range(20) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msgs         nstages src_delay sink_delay"),
  [ "basic_stall0.0_0x0",  basic_msgs,  4,      0,        0          ],
  [ "random_stall0.0_0x0", random_msgs, 4,      0,        0          ],
  [ "random_stall0.0_9x0", random_msgs, 4,      9,        0          ],
  [ "random_stall0.0_0x9", random_msgs, 4,      0,        9          ],
  [ "random_stall0.0_9x9", random_msgs, 4,      9,        9          ],
  [ "random_stall0.5_0x0", random_msgs, 4,      0,        0          ],
  [ "random_stall0.5_9x0", random_msgs, 4,      9,        0          ],
  [ "random_stall0.5_0x9", random_msgs, 4,      0,        9          ],
  [ "random_stall0.5_9x9", random_msgs, 4,      9,        9          ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( test_params.msgs, test_params.nstages,
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )
