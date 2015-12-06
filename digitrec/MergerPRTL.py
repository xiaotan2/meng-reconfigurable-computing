#====================================================================
# MergerPRTL
#====================================================================
from pymtl      import *
from FindMaxMin import *

import math

class MergerPRTL( Model ):

  # Constructor
  def __init__( s, reducer_num = 10, nbits = 8 ) :

    addr_nbits = int( math.ceil( math.log( reducer_num, 2 ) ) )

    # interface
    s.in_      = [ InPort( nbits ) for _ in range( reducer_num ) ]
    s.out      = OutPort( addr_nbits )

    # find the minimum sum output digit number
    s.findmin  = FindMinIdx( nbits, reducer_num )

    for i in xrange( reducer_num ):
      s.connect_pairs( s.findmin.in_[i], s.in_[i] )

    s.connect( s.findmin.idx, s.out )

