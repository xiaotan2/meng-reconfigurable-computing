#=========================================================================
# Adder Wrapper
#=========================================================================


from pymtl  import *

class Adder ( VerilogModel ):
  
  vprefix    = ""
  vlinetrace = True

  def __init__ ( s ):
   
    s.in0 = InPort  ( Bits(16) )
    s.in1 = InPort  ( Bits(16) ) 
    s.out = OutPort ( Bits(16) )

    s.set_ports({
      'in0'   :  s.in0,
      'in1'   :  s.in1,
      'out'   :  s.out, 
    })

  def line_trace( s ):
    return "{} () {} () {}".format( s.in0, s.in1, s.out)

