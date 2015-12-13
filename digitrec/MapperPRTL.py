#=========================================================================
# Mapper
#=========================================================================

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from DistancePRTL  import Adder, Xor, AdderTree
from MapperMsg     import MapperReqMsg, MapperRespMsg

DATA_NBITS     = 49
DIGIT_NBITS    = 4
TYPE_NBITS     = 1
DISTANCE_NBITS = 6

class MapperPRTL( Model ):

  def __init__( s ):

    s.in0 = InPort  ( 49 )
    s.in1 = InPort  ( 49 )
    s.out = OutPort ( 6  )

    s.x = m = Xor( 49 )
    s.connect_dict({
      m.in0: s.in0,
      m.in1: s.in1,
    })

    s.d = m = AdderTree()
    for i in xrange(49):
      s.connect( s.x.out[i], m.in_[i] )
    s.connect( m.out, s.out )
 

  def line_trace( s ):
    return "train({}) test({}) => dist({})".format( s.in0, s.in1, s.out )
