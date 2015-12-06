#====================================================================
# AdderTree
#====================================================================
from pymtl      import *

import math

class Adder( Model ):
   
  def __init__( s, nbits = 8 ):
    
    s.in0 = InPort ( nbits )
    s.in1 = InPort ( nbits )
    s.out = OutPort( nbits )

    @s.combinational
    def comb_logic():
      s.out = s.in0 + s.in1
      

class AdderTree( Model ):

  def __init__( s, nbits = 6, k = 3 ):

    sum_nbits = int( math.ceil( math.log( (2**nbits-1)*k, 2  ) ) )

    # interface
    s.in_   = [ InPort( nbits ) for _ in range( k ) ]
    s.out   = OutPort( sum_nbits )

    # muxs and cmps
    s.adders  = [ Adder( sum_nbits )  for i in xrange( k-1 ) ]

    s.tmp     = Wire[k]( Bits( sum_nbits ) )

    @s.combinational
    def comb_logic():
      for ( i in xrange( k ) ):
        s.tmp[i].value = zext( s.in_[i], sum_bits )

    s.connect_wire( s.adders[0].in0, s.tmp[0] )
    s.connect_wire( s.adders[0].in1, s.tmp[1] )

    if ( k > 2 ) :
      for ( i in xrange( 1, k-1 ) ):
        s.connect_pairs(
          s.adders[i].in0, s.adders[i-1].out,
          s.adders[i].in1, s.tmp[i+1]
        )

    s.connect( s.adders[k-2].out, s.out )






