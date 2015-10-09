#=========================================================================
# Counter
#=========================================================================

from pymtl     import *
from pclib.rtl import RegRst

class Counter( Model ):

  def __init__( s, nbits, count_reset_value=0, max_count=0 ):

    if   max_count == 0 : s.max_count = 2**nbits - 1
    elif max_count == 0 : s.max_count = max_count

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.increment     = InPort( 1 )
    s.decrement     = InPort( 1 )

    s.count         = OutPort( nbits )
    s.count_is_zero = OutPort( 1 )
    s.count_is_max  = OutPort( 1 )

    #---------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------

    s.count_next   = Wire( nbits )
    s.do_increment = Wire( 1 )
    s.do_decrement = Wire( 1 )

    s.count_reg = RegRst( nbits, count_reset_value )

    s.connect( s.count_reg.in_, s.count_next )
    s.connect( s.count_reg.out, s.count      )

    @s.combinational
    def comb():

      s.do_increment.value = \
        ( s.increment & ~s.decrement & ( s.count < s.max_count ) )

      s.do_decrement.value = \
        ( ~s.increment & s.decrement & ( s.count > 0 ) )

      s.count_next.value = 0
      if   s.do_increment: s.count_next.value = ( s.count + 1 )
      elif s.do_decrement: s.count_next.value = ( s.count - 1 )
      else               : s.count_next.value = s.count

      s.count_is_zero.value = ( s.count_reg.out == 0 )
      s.count_is_max.value  = ( s.count_reg.out == s.max_count )
