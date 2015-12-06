#====================================================================
# FindMaxMin
#====================================================================
from pymtl      import *
from pclib.rtl  import GtComparator, LtComparator, Mux

import math

class FindMax( Model ):

  def __init__( s, nbits = 6, k = 3 ):   

    # interface 
    s.in_   = [ InPort( nbits ) for _ in range( k ) ]
    s.out   = OutPort( nbits )

    # muxs and cmps
    s.muxs  = [ Mux( nbits, 2 )       for i in xrange( k-1 ) ]
    s.cmps  = [ GtComparator( nbits ) for i in xrange( k-1 ) ]

    s.connect_wire( s.muxs[0].in_[0], s.in_[0]      )
    s.connect_wire( s.muxs[0].in_[1], s.in_[1]      )
    s.connect_wire( s.cmps[0].in0,    s.in_[1]      )
    s.connect_wire( s.cmps[0].in1,    s.in_[0]      )
    s.connect_wire( s.cmps[0].out,    s.muxs[0].sel )

    if k > 2:
      for i in xrange( 1, k-1 ):
        s.connect_pairs(
          s.muxs[i].in_[0], s.muxs[i-1].out,
          s.muxs[i].in_[1], s.in_[i+1],
          s.muxs[i].sel,    s.cmps[i  ].out,
          s.cmps[i].in0,    s.in_[i+1],
          s.cmps[i].in1,    s.muxs[i-1].out
        )
  
    s.connect( s.muxs[k-2], s.out )


  def line_trace( s ):

    return "{}".format(
      s.mux[0].sel
    )


class FindMaxIdx( Model ):

  def __init__( s, nbits = 6, k = 3 ):

    addr_nbits = int( math.ceil( math.log( k, 2 ) ) )

    # interface
    s.in_   = [ InPort( nbits ) for _ in range( k ) ]
    s.out   = OutPort( nbits )
    s.idx   = OutPort( addr_nbits )

    # muxs and cmps
    s.muxs  = [ Mux( nbits, 2 )       for i in xrange( k-1 ) ]
    s.cmps  = [ GtComparator( nbits ) for i in xrange( k-1 ) ]

    s.connect_wire( s.muxs[0].in_[0], s.in_[0]      )
    s.connect_wire( s.muxs[0].in_[1], s.in_[1]      )
    s.connect_wire( s.cmps[0].in0,    s.in_[1]      )
    s.connect_wire( s.cmps[0].in1,    s.in_[0]      )
    s.connect_wire( s.cmps[0].out,    s.muxs[0].sel )

    if k > 2:
      for i in xrange( 1, k-1 ):
        s.connect_pairs(
          s.muxs[i].in_[0], s.muxs[i-1].out,
          s.muxs[i].in_[1], s.in_[i+1],
          s.muxs[i].sel,    s.cmps[i  ].out,
          s.cmps[i].in0,    s.in_[i+1],
          s.cmps[i].in1,    s.muxs[i-1].out
        )

    @s.combinational
    def comb_logic():
    
      for i in range( k-1 ):
        if ( s.muxs[i].sel == 1 ):
          s.idx.value = i
        else 
          s.idx.value = 0

    s.connect( s.muxs[k-2], s.out )
  
  def line_trace( s ):

    return "{}".format(
      s.mux[0].sel
    )

class FindMin( Model ):
 
  def __init__( s, nbits = 6, k = 3 ):

    # interface
    s.in_   = [ InPort( nbits ) for _ in range( k ) ]
    s.out   = OutPort( nbits )

    # muxs and cmps
    s.muxs  = [ Mux( nbits, 2 )       for i in xrange( k-1 ) ]
    s.cmps  = [ LtComparator( nbits ) for i in xrange( k-1 ) ]

    s.connect_wire( s.muxs[0].in_[0], s.in_[0]      )
    s.connect_wire( s.muxs[0].in_[1], s.in_[1]      )
    s.connect_wire( s.cmps[0].in0,    s.in_[1]      )
    s.connect_wire( s.cmps[0].in1,    s.in_[0]      )
    s.connect_wire( s.cmps[0].out,    s.muxs[0].sel )

    if k > 2:
      for i in xrange( 1, k-1 ):
        s.connect_pairs(
          s.muxs[i].in_[0], s.muxs[i-1].out,
          s.muxs[i].in_[1], s.in_[i+1],
          s.muxs[i].sel,    s.cmps[i  ].out,
          s.cmps[i].in0,    s.in_[i+1],
          s.cmps[i].in1,    s.muxs[i-1].out
        )

    s.connect( s.muxs[k-2], s.out )


  def line_trace( s ):

    return "{}".format(
      s.mux[0].sel
    )

class FindMinIdx( Model ):

  def __init__( s, nbits = 8, k = 10 ):

    addr_nbits = int( math.ceil( math.log( k, 2 ) ) )

    # interface
    s.in_   = [ InPort( nbits ) for _ in range( k ) ]
    s.out   = OutPort( nbits )
    s.idx   = OutPort( addr_nbits )

    # muxs and cmps
    s.muxs  = [ Mux( nbits, 2 )       for i in xrange( k-1 ) ]
    s.cmps  = [ LtComparator( nbits ) for i in xrange( k-1 ) ]

    s.connect_wire( s.muxs[0].in_[0], s.in_[0]      )
    s.connect_wire( s.muxs[0].in_[1], s.in_[1]      )
    s.connect_wire( s.cmps[0].in0,    s.in_[1]      )
    s.connect_wire( s.cmps[0].in1,    s.in_[0]      )
    s.connect_wire( s.cmps[0].out,    s.muxs[0].sel )

    if k > 2:
      for i in xrange( 1, k-1 ):
        s.connect_pairs(
          s.muxs[i].in_[0], s.muxs[i-1].out,
          s.muxs[i].in_[1], s.in_[i+1],
          s.muxs[i].sel,    s.cmps[i  ].out,
          s.cmps[i].in0,    s.in_[i+1],
          s.cmps[i].in1,    s.muxs[i-1].out
        )

    @s.combinational
    def comb_logic():

      for i in range( k-1 ):
        if ( s.muxs[i].sel == 1 ):
          s.idx.value = i
        else
          s.idx.value = 0

    s.connect( s.muxs[k-2], s.out )

  def line_trace( s ):

    return "{}".format(
      s.mux[0].sel
    )
