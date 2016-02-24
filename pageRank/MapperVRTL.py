#=========================================================================
# Mapper RTL Model
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle

class MapperVRTL( VerilogModel ):

  # Constructor

  def __init__( s, nbits = 32 ):

    # Interface

    s.in0   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.in1   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.in2   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.in3   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.out   = OutPort ( Bits(nbits)   )

    # Verilog ports

    s.set_ports({
      'r_0'         : s.in0,
      'g_0'         : s.in1,
      'r_1'         : s.in2,
      'g_1'         : s.in3,
      'out'         : s.out
    })


  def line_trace( s ):
    return "in0 {} in1 {} in2 {} in3 {} => out {}".format( s.in0, s.in1, s.in2, s.in3, s.out )
