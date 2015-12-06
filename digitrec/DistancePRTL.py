#=========================================================================
# Module
#=========================================================================

from pymtl         import *

#=========================================================================
# Adder
#=========================================================================
class Adder( Model ):

  def __init__( s, ibits = 1, obits = 1 ):
    
    s.in0 = InPort  ( ibits )
    s.in1 = InPort  ( ibits )
    s.out = OutPort ( obits )
  
    @s.combinational
    def comb_logic():
      t0 = zext( s.in0, obits )
      t1 = zext( s.in1, obits )
      s.out.value = t0 + t1
    def line_trace( s ):
      return "{} {} {}".format( s.in0, s.in1, s.out )


#=========================================================================
# Xor
#=========================================================================
class Xor( Model ):
  
  def __init__( s, nbits =1 ): 

    s.in0 = InPort  ( nbits )
    s.in1 = InPort  ( nbits )
    s.out = OutPort ( nbits )

    @s.combinational
    def comb_logic():
      s.out.value = s.in0 ^ s.in1

#=========================================================================
# AdderTree
#=========================================================================
class AdderTree( Model ):

  def __init__( s ):
    
    s.in_ = InPort[49]( 1 )
    s.out = OutPort   ( 6 )

    s.adder1 = [ Adder( ibits = 1, obits = 2 ) for i in xrange(24) ]
    for i in xrange(24):
      s.connect_pairs(
        s.in_[2*i + 0],         s.adder1[i].in0,
        s.in_[2*i + 1],         s.adder1[i].in1      
      )

    s.adder2 = [ Adder( ibits = 2, obits = 3 ) for i in xrange(12) ]
    for i in xrange(12):
      s.connect_pairs(
        s.adder1[2*i + 0].out,  s.adder2[i].in0,
        s.adder1[2*i + 1].out,  s.adder2[i].in1
      )

    s.adder3 = [ Adder( ibits = 3, obits = 4 ) for i in xrange(6) ]
    for i in xrange(6):
      s.connect_pairs(
        s.adder2[2*i + 0].out,  s.adder3[i].in0,
        s.adder2[2*i + 1].out,  s.adder3[i].in1
      )

    s.adder4 = [ Adder( ibits = 4, obits = 5 ) for i in xrange(3) ]
    for i in xrange(3):
      s.connect_pairs(
        s.adder3[2*i + 0].out,  s.adder4[i].in0,
        s.adder3[2*i + 1].out,  s.adder4[i].in1
      )
    
    s.adder5_in = Wire(5)
    @s.combinational
    def comb_logic():
      s.adder5_in.value = zext( s.in_[48], 5 )

    s.adder5 = [ Adder( ibits = 5, obits = 6 ) for i in xrange(2) ]
    s.connect_pairs(
      s.adder4[0].out,  s.adder5[0].in0,
      s.adder4[1].out,  s.adder5[0].in1,
      s.adder4[2].out,  s.adder5[1].in0,
      s.adder5_in,      s.adder5[1].in1
      )

    s.adder6 = Adder( ibits = 6, obits = 6 )
    s.connect_pairs(
      s.adder5[0].out,  s.adder6.in0,
      s.adder5[1].out,  s.adder6.in1,
      s.adder6.out,     s.out
    )

    def line_trace( s ):
      return "{} {} {}".format( s.adder1[0].out, s.adder1[1].out, s.adder1[23].out )

