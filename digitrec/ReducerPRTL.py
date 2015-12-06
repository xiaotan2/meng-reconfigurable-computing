#====================================================================
# Reducer
#====================================================================
from pymtl      import *
from pclib.rtl  import GtComparator, LtComparator, Mux
from FindMaxMin import FindMax

import math

class ReducerPRTL( Model ):

  # Constructor
  def __init__( s, nbits = 6, k = 3, rst_value = 50 ):

    addr_nbits = int( math.ceil( math.log( k, 2 ) ) )

    # Regists
    s.rd_addr  = Wire[k]( Bits(addr_nbits ) )
    s.rd_data  = Wire[k]( Bits(nbits      ) )

    s.wr_addr  = Wire[k]( Bits(addr_nbits ) )
    s.wr_data  = Wire[k]( Bits(nbits      ) )
    s.wr_en    = Wire[k]( Bits(1          ) )

    s.regs     = [ RegEnRst( nbits, rst_value ) for i in xrange( k ) ]

    for i in xrange( k ):
      s.connect_pairs(
        s.regs[i].in_, s.wr_data[i],
        s.regs[i].out, s.rd_data[i],
        s.regs[i].en , s.wr_en[i]
      )

