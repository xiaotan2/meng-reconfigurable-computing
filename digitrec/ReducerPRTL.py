#====================================================================
# Reducer
#====================================================================
from pymtl      import *
from pclib.rtl  import RegEnRst, LtComparator, Mux
from FindMaxMin import *
from AdderTree  import *

import math

class ReducerPRTL( Model ):

  # Constructor
  def __init__( s, mapper_num = 3, nbits = 6, k = 3, rst_value = 50 ):

    addr_nbits = int( math.ceil( math.log( k, 2 ) ) )
    sum_nbits  = int( math.ceil( math.log( (2**nbits-1)*k, 2  ) ) )

    # interface
    s.in_      = [ InPort( nbits ) for _ in range( mapper_num ) ]
    s.out      = OutPort( sum_nbits )

    # internal wires
    s.min_dist = Wire( Bits( nbits      ) )
    s.max_dist = Wire( Bits( nbits      ) )
    s.max_idx  = Wire( Bits( addr_nbits ) )
    s.isLess   = Wire( Bits( 1          ) )

    s.rd_data  = Wire[k]( Bits(nbits      ) )
    s.wr_addr  = Wire[k]( Bits(addr_nbits ) )
    s.wr_en    = Wire[k]( Bits(1          ) )
   

    # find min of inputs
    s.findmin  = FindMin( nbits, mapper_num )

    for i in xrange( mapper_num ):
      s.connect_pairs( s.findmin.in_[i], s.in_[i] )

    s.connect_pairs( s.findmin.out, s.min_dist )

    # find max in knn_table
    s.findmax  = FindMaxIdx( nbits, k )
    
    for i in xrange( k ):
      s.connect_pairs( s.findmax.in_[i], s.rd_data[i] )

    s.connect_pairs( s.findmax.out, s.max_dist ) 
    s.connect_pairs( s.findmax.idx, s.max_idx  ) 

    # compare min_dist and max_dist
    s.cmp      = LtComparator( nbits )
    s.connect_pairs( 
      s.cmp.in0, s.min_dist,
      s.cmp.in1, s.max_dist,
      s.cmp.out, s.isLess
    )

    # choose the smaller one write back
    @s.combinational
    def comb_logic():
      for i in xrange ( k ):
        if ( i == s.max_idx ):
          s.wr_en[i].value = s.isLess
        else:
          s.wr_en[i].value = 0

    # Registers
    s.regs     = [ RegEnRst( nbits, rst_value ) for i in xrange( k ) ]

    for i in xrange( k ):

      s.connect_pairs(
        s.regs[i].in_, s.min_dist,
        s.regs[i].out, s.rd_data[i],
        s.regs[i].en , s.wr_en[i]
      )

    # sum of knn_table 
    s.addertree = AdderTree( nbits, k )
    for i in xrange( k ):
      s.connect_pairs( s.addertree.in_[i], s.rd_data[i] )

    s.connect( s.addertree.out, s.out )


  def line_trace( s ):
    return "in_({} {} {}) min_dist({}) max_dist({}) isLess({}) data({} {} {}) wr_en({} {} {}) sum({})".format(
      s.in_[0], s.in_[1], s.in_[2],
      s.min_dist, s.max_dist, s.isLess, 
      s.rd_data[0], s.rd_data[1], s.rd_data[2],
      s.wr_en[0], s.wr_en[1], s.wr_en[2],
      s.out
    ) 
