#=========================================================================
# Mapper RTL Model
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle

class MapperVRTL( VerilogModel ):

  # Constructor

  def __init__( s, nbits = 32 ):

    # Interface

    s.r_0   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.g_0   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.r_1   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.g_1   = InPort  ( Bits(nbits)   )#[ InPort  ( nbits ) for _ in range( n ) ]
    s.out   = OutPort ( Bits(nbits)   )

    # Verilog ports

    s.set_ports({
      'clk'         : s.clk,
      'reset'       : s.reset,

      'r_0'         : s.r_0,
      'g_0'         : s.g_0,
      'r_1'         : s.r_1,
      'g_1'         : s.g_1,
      'out'         : s.out
    })


  def line_trace( s ):
    return "r_0 {} * g_0 {} + r_1 {} * g_1 {} => out {}".format( s.r_0, s.g_0, s.r_1, s.g_1, s.out )
