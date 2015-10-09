#=========================================================================
# Pipeline.py
#=========================================================================
# Models an inelastic pipeline with input and output valrdy bundles. This
# model helps in testing accelerators that need to be integrated to the
# processor pipeline.

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.cl   import OutValRdyInelasticPipeAdapter, InValRdyRandStallAdapter

#-------------------------------------------------------------------------
# Pipeline
#-------------------------------------------------------------------------

class Pipeline( Model ):

  def __init__( s, dtype, nstages ):

    s.in_   = InValRdyBundle  ( dtype )
    s.out   = OutValRdyBundle ( dtype )

    s.in_q  = InValRdyRandStallAdapter      ( s.in_,       0 )
    s.out_q = OutValRdyInelasticPipeAdapter ( s.out, nstages )

    @s.tick_cl
    def block():
      s.in_q.xtick()
      s.out_q.xtick()
      if not s.in_q.empty() and not s.out_q.full():
        s.out_q.enq( s.in_q.deq() )

  def line_trace( s ):
    return "{}(){}".format( s.in_, s.out )
