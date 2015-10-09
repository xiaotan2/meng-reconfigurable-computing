#=======================================================================
# StoreBuffer
#=======================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import RegEn, RegisterFile

#-----------------------------------------------------------------------
# StoreBuffer
#-----------------------------------------------------------------------
class StoreBuffer( Model ):

  def __init__( s, num_entries, dtype ):

    s.enq              = InValRdyBundle ( dtype )
    s.deq              = OutValRdyBundle( dtype )
    s.num_free_entries = OutPort( get_nbits(num_entries) )
    s.squash           = InPort( 1 )
    s.advance_deq_ptr  = InPort( clog2( num_entries ) )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = StoreBufferCtrl ( num_entries             )
    s.dpath = StoreBufferDpath( num_entries, dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val,          s.enq.val          )
    s.connect( s.ctrl.enq_rdy,          s.enq.rdy          )
    s.connect( s.ctrl.deq_val,          s.deq.val          )
    s.connect( s.ctrl.deq_rdy,          s.deq.rdy          )
    s.connect( s.ctrl.num_free_entries, s.num_free_entries )
    s.connect( s.ctrl.squash,           s.squash           )
    s.connect( s.ctrl.advance_deq_ptr,  s.advance_deq_ptr  )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg    )
    s.connect( s.dpath.deq_bits, s.deq.msg    )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen   )
    s.connect( s.dpath.waddr,    s.ctrl.waddr )
    s.connect( s.dpath.raddr,    s.ctrl.raddr )

  def line_trace( s ):
    return "{} () {}".format( s.enq, s.deq )

#-----------------------------------------------------------------------
# StoreBufferDpath
#-----------------------------------------------------------------------
class StoreBufferDpath( Model ):

  def __init__( s, num_entries, dtype ):

    s.enq_bits  = InPort  ( dtype )
    s.deq_bits  = OutPort ( dtype )

    # Control signal (ctrl -> dpath)
    addr_nbits  = clog2( num_entries )
    s.wen       = InPort  ( 1 )
    s.waddr     = InPort  ( addr_nbits )
    s.raddr     = InPort  ( addr_nbits )

    # Queue storage

    s.queue = RegisterFile( dtype, num_entries )

    # Connect queue storage

    s.connect( s.queue.rd_addr[0], s.raddr    )
    s.connect( s.queue.rd_data[0], s.deq_bits )
    s.connect( s.queue.wr_en,      s.wen      )
    s.connect( s.queue.wr_addr,    s.waddr    )
    s.connect( s.queue.wr_data,    s.enq_bits )

#-----------------------------------------------------------------------
# StoreBufferCtrl
#-----------------------------------------------------------------------
class StoreBufferCtrl( Model ):

  def __init__( s, num_entries ):

    s.num_entries = num_entries
    addr_nbits    = clog2( num_entries )

    # Interface Ports

    s.enq_val          = InPort  ( 1 )
    s.enq_rdy          = OutPort ( 1 )
    s.deq_val          = OutPort ( 1 )
    s.deq_rdy          = InPort  ( 1 )
    s.num_free_entries = OutPort ( get_nbits( num_entries ) )
    s.squash           = InPort  ( 1 )
    s.advance_deq_ptr  = InPort  ( addr_nbits )

    # Control signal (ctrl -> dpath)
    s.wen              = OutPort ( 1 )
    s.waddr            = OutPort ( addr_nbits )
    s.raddr            = OutPort ( addr_nbits )

    # Wires

    s.full             = Wire ( 1 )
    s.empty            = Wire ( 1 )
    s.do_enq           = Wire ( 1 )
    s.do_deq           = Wire ( 1 )
    s.enq_ptr          = Wire ( addr_nbits )
    s.deq_ptr          = Wire ( addr_nbits )
    s.enq_ptr_next     = Wire ( addr_nbits )
    s.deq_ptr_next     = Wire ( addr_nbits )
    s.enq_ptr_inc      = Wire ( addr_nbits )
    s.deq_ptr_inc      = Wire ( addr_nbits )
    s.full_next_cycle  = Wire ( 1 )

    s.last_idx         = num_entries - 1

    @s.combinational
    def comb():

      # set output signals

      s.empty.value   = not s.full and (s.enq_ptr == s.deq_ptr)

      s.enq_rdy.value = not s.full
      s.deq_val.value = not s.empty

      # only enqueue/dequeue if valid and ready

      s.do_enq.value = s.enq_rdy and s.enq_val
      s.do_deq.value = s.deq_rdy and s.deq_val

      # set control signals

      s.wen.value     = s.do_enq
      s.waddr.value   = s.enq_ptr
      s.raddr.value   = s.deq_ptr

      # enq ptr incrementer

      if s.enq_ptr == s.last_idx: s.enq_ptr_inc.value = 0
      else:                       s.enq_ptr_inc.value = s.enq_ptr + 1

      # deq ptr incrementer

      if s.deq_ptr == s.last_idx: s.deq_ptr_inc.value = 0
      else:                       s.deq_ptr_inc.value = s.deq_ptr + 1

      # set the next ptr value

      if s.do_enq: s.enq_ptr_next.value = s.enq_ptr_inc
      else:        s.enq_ptr_next.value = s.enq_ptr

      if   s.squash: s.deq_ptr_next.value = s.advance_deq_ptr
      elif s.do_deq: s.deq_ptr_next.value = s.deq_ptr_inc
      else:          s.deq_ptr_next.value = s.deq_ptr

      # number of free entries calculation

      if   s.reset:
        s.num_free_entries.value = s.num_entries
      elif s.full:
        s.num_free_entries.value = 0
      elif s.empty:
        s.num_free_entries.value = s.num_entries
      elif s.enq_ptr > s.deq_ptr:
        s.num_free_entries.value = s.num_entries - ( s.enq_ptr - s.deq_ptr )
      elif s.deq_ptr > s.enq_ptr:
        s.num_free_entries.value = s.deq_ptr - s.enq_ptr

      s.full_next_cycle.value = (s.do_enq and not s.do_deq and
                                (s.enq_ptr_next == s.deq_ptr))

    @s.posedge_clk
    def seq():

      if s.reset: s.deq_ptr.next = 0
      else:       s.deq_ptr.next = s.deq_ptr_next

      if s.reset: s.enq_ptr.next = 0
      else:       s.enq_ptr.next = s.enq_ptr_next

      if   s.reset:               s.full.next = 0
      elif s.full_next_cycle:     s.full.next = 1
      elif (s.do_deq and s.full): s.full.next = 0
      else:                       s.full.next = s.full
