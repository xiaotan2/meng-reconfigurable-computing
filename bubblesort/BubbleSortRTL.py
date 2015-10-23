from pymtl        import *
from pclib.rtl    import Mux, RegRst
from pclib.ifcs import XcelMsg, MemMsg, MemReqMsg4B, MemRespMsg4B
from pclib.rtl  import SingleElementBypassQueue, SingleElementPipelinedQueue, TwoElementBypassQueue
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.fl   import InValRdyQueueAdapter, OutValRdyQueueAdapter
from pclib.fl   import ListMemPortAdapter

from xcel.XcelMsg      import XcelReqMsg, XcelRespMsg
from xmem.MemMsgFuture import MemMsg, MemReqMsg, MemRespMsg

# Constant

MUX_IN1 = 0
MUX_IN2 = 1
COUNTER_BITS = 8
READ_CYCLE = 1
WRITE_CYCLE = 0

class BubbleSortRTL( Model ) :

  # Constructor

  def __init__( s, mem_msg=MemMsg(8,32,32) ):

    # Interface

    s.xcelreq           = InValRdyBundle  ( XcelReqMsg() )
    s.xcelresp          = OutValRdyBundle ( XcelRespMsg() )
    s.memreq            = OutValRdyBundle ( mem_msg.req )
    s.memresp           = InValRdyBundle  ( mem_msg.resp )

    s.dpath             = BSDatapathRTL()
    s.ctrl              = BSControlUnitRTL()

    s.duamemreq         = OutValRdyBundle ( mem_msg.req )
    s.duamemresp        = InValRdyBundle  ( mem_msg.resp )

    # Bypass queues
    s.xcelreq_queue     = SingleElementPipelinedQueue( XcelReqMsg() )
    s.memreq_queue      = SingleElementBypassQueue( MemReqMsg(8,32,32) )
    s.memresp_queue     = SingleElementBypassQueue( MemRespMsg(8,32) )
    s.duamemreq_queue   = SingleElementBypassQueue( MemReqMsg(8,32,32) )
    s.duamemresp_queue  = SingleElementBypassQueue( MemRespMsg(8,32) )
    s.connect_pairs(
      s.memreq_queue.deq,  s.memreq,
      s.xcelreq_queue.enq, s.xcelreq,
      s.memresp_queue.enq, s.memresp,
      s.duamemreq_queue.deq,   s.duamemreq,
      s.duamemresp_queue.enq,  s.duamemresp
    )

    # Connect datapath signals
    s.connect(s.memresp_queue.deq.msg.data, s.dpath.mem_rdata2)
    s.connect(s.duamemresp_queue.deq.msg.data, s.dpath.mem_rdata1)
    s.connect(s.dpath.mem_wdata1, s.duamemreq_queue.enq.msg.data)
    s.connect(s.dpath.mem_wdata2, s.memreq_queue.enq.msg.data)

    # Connect ctl unit signals to XCelReqMsg
    s.connect_pairs(
      s.ctrl.xcelreq_val, s.xcelreq_queue.deq.val,
      s.ctrl.xcelreq_rdy, s.xcelreq_queue.deq.rdy,
      s.ctrl.xcelresp_val, s.xcelresp.val,
      s.ctrl.xcelresp_rdy, s.xcelresp.rdy,
      s.ctrl.xcelreq_msgtype, s.xcelreq_queue.deq.msg.type_,
      s.ctrl.xcelreq_msgdata, s.xcelreq_queue.deq.msg.data,
      s.ctrl.xcelreq_msgaddr, s.xcelreq_queue.deq.msg.raddr,
      s.ctrl.xcelresp_msgdata, s.xcelresp.msg.data,
      s.ctrl.xcelresp_msgtype, s.xcelresp.msg.type_
    )

    # Connect ctl unit signals to MemMsg
    s.connect_pairs(
      s.ctrl.memreq_val, s.memreq_queue.enq.val,
      s.ctrl.memreq_rdy, s.memreq_queue.enq.rdy,
      s.ctrl.memreq_msgtype, s.memreq_queue.enq.msg.type_,
      s.ctrl.memreq_msgaddr, s.memreq_queue.enq.msg.addr,
      s.ctrl.memresp_val, s.memresp_queue.deq.val,
      s.ctrl.memresp_rdy, s.memresp_queue.deq.rdy,
    )

    # Connect dual Mem Port to ctrl unit
    s.connect_pairs(
      s.ctrl.dualmemreq_val, s.duamemreq_queue.enq.val,
      s.ctrl.dualmemreq_rdy, s.duamemreq_queue.enq.rdy,
      s.ctrl.dualmemreq_msgtype, s.duamemreq_queue.enq.msg.type_,
      s.ctrl.dualmemreq_msgaddr, s.duamemreq_queue.enq.msg.addr,
      s.ctrl.dualmemresp_val, s.duamemresp_queue.deq.val,
      s.ctrl.dualmemresp_rdy, s.duamemresp_queue.deq.rdy,
    )

    # Connect status/control signals
    s.connect_auto( s.dpath, s.ctrl )

    @s.combinational
    def connector():
      s.memreq.msg.opaque.value = 0
      s.memreq.msg.len.value = 0

  def line_trace( s ):

    xcel_req_str  = " x_req:v{}$r{}$a{}$d{}$t{}".format(
                            s.xcelreq.val, s.xcelreq.rdy, 
                            s.xcelreq_queue.deq.msg.raddr, 
                            s.xcelreq_queue.deq.msg.data, 
                            s.xcelreq_queue.deq.msg.type_)

    xcel_resp_str = " x_resp:v{}$r{}$d{}$t{}".format(
                            s.xcelresp.val, s.xcelresp.rdy, 
                            s.xcelresp.msg.data, s.xcelresp.msg.type_)

    read_req_str  = " r_req:v{}|r{}|a{}|t{}".format(
                            s.memreq_queue.enq.val, 
                            s.memreq_queue.enq.rdy, 
                            s.memreq_queue.enq.msg.addr, 
                            s.memreq_queue.enq.msg.type_)

    read_resp_str = " r_resp:v{}|r{}|d{}".format(
                            s.memresp.val, s.memresp.rdy, 
                            s.memresp.msg.data)

    write_req_str = " w_req:a{}|d{}".format(
                            s.memreq_queue.enq.msg.addr, 
                            s.memreq_queue.enq.msg.data)

    debug_str     = " debug{}|{}|{}".format(
                            s.ctrl.state.out, s.ctrl.counteri, 
                            s.ctrl.countero)

    mux_str       = " m1{}|m2{}|m3{}|m4{}".format(
                            s.dpath.reg_mux1_out, 
                            s.dpath.reg_mux2_out, 
                            s.dpath.reg_mux3_out, 
                            s.dpath.reg_mux4_out)

    mem_inter     = (read_req_str + "$$" + 
                     read_resp_str + "$$" + 
                     write_req_str) 

    line_str = (debug_str)
    return line_str

class BSDatapathRTL( Model ):

  def __init__(s):

    #--------------------------------------------------------------
    # Interface
    #--------------------------------------------------------------

    s.mem_rdata1                = InPort( Bits(32) )
    s.mem_rdata2                = InPort( Bits(32) )
    s.mem_wdata1                = OutPort( Bits(32) )
    s.mem_wdata2                = OutPort( Bits(32) )

    s.RR                        = InPort( Bits(1) )

    #--------------------------------------------------------------
    # Registers
    #--------------------------------------------------------------

    # Register first
    s.reg_fir                   = Wire( Bits(32) ) # r1

    # Flag
    s.swap                      = Wire( Bits(1) )

    # Mux Output Registers
    s.reg_mux1_out              = Wire( Bits(32) )
    s.reg_mux2_out              = Wire( Bits(32) )
    s.reg_mux3_out              = Wire( Bits(32) )
    s.reg_mux4_out              = Wire( Bits(32) )
    s.reg_mux5_out              = Wire( Bits(32) )
    s.reg_mux6_out              = Wire( Bits(32) )

    #--------------------------------------------------------------
    # Ticking Concurrent Blocks
    #--------------------------------------------------------------

    @s.tick_rtl
    def updateRegister():
      if s.reset:
        s.reg_fir.next          = 0
      else:
        s.reg_fir.next          = s.reg_mux4_out

    #--------------------------------------------------------------
    # Combinational Logic
    #--------------------------------------------------------------

    @s.combinational
    def comb_logic():
      # Comparator
      if(s.mem_rdata2 < s.reg_mux1_out):
        s.swap.value            = 1
      else:
        s.swap.value            = 0

      # Connect Output port
      s.mem_wdata1.value    = s.reg_mux2_out
      s.mem_wdata2.value    = s.reg_mux3_out

    # Instantiate Mux for choosing register2 to be compared
    s.mux_1 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.RR,
      m.in_[ WRITE_CYCLE ]   : s.reg_fir,
      m.in_[ READ_CYCLE ]    : s.mem_rdata1,
      m.out                  : s.reg_mux1_out,
    })

    # Instantiate Mux for choosing write memory data 1
    s.mux_2 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.swap,
      m.in_[ MUX_IN1 ]       : s.reg_mux1_out,
      m.in_[ MUX_IN2 ]       : s.mem_rdata2,
      m.out                  : s.reg_mux2_out,
    })

    # Instantiate Mux for choosing write memory data 2
    s.mux_3 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.swap,
      m.in_[ MUX_IN1 ]       : s.mem_rdata2,
      m.in_[ MUX_IN2 ]       : s.reg_mux1_out,
      m.out                  : s.reg_mux3_out,
    })

    # Instantiate Mux for choosing register1 to store
    s.mux_4 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.swap,
      m.in_[ MUX_IN1 ]       : s.mem_rdata2,
      m.in_[ MUX_IN2 ]       : s.reg_mux1_out,
      m.out                  : s.reg_mux4_out,
    })

class BSControlUnitRTL( Model ) :

  # Constructor

  def __init__( s ):

    # Interface
    s.base                   = Wire  ( Bits(32) )
    s.size                   = Wire  ( Bits(32) )

    s.xcelreq_val            = InPort(1)
    s.xcelreq_rdy            = OutPort(1)
    s.xcelresp_val           = OutPort(1)
    s.xcelresp_rdy           = InPort(1)

    s.memreq_val             = OutPort(1)
    s.memreq_rdy             = InPort(1)
    s.memresp_val            = InPort(1)
    s.memresp_rdy            = OutPort(1)
    s.memreq_msgtype         = OutPort(3)
    s.memreq_msgaddr         = OutPort(32)

    s.xcelreq_msgtype        = InPort(1)
    s.xcelreq_msgaddr        = InPort(5)
    s.xcelreq_msgdata        = InPort(32)
    s.xcelresp_msgtype       = OutPort(1)
    s.xcelresp_msgdata       = OutPort(32)

    # Dual Mem Port signals
    s.dualmemreq_val         = OutPort(1)
    s.dualmemreq_rdy         = InPort(1)
    s.dualmemresp_val        = InPort(1)
    s.dualmemresp_rdy        = OutPort(1)
    s.dualmemreq_msgtype     = OutPort(3)
    s.dualmemreq_msgaddr     = OutPort(32)

    s.RR                     = OutPort(1)

    # Counter Signals
    s.counteri               = Wire ( Bits(COUNTER_BITS) )
    s.countero               = Wire ( Bits(COUNTER_BITS) )

    # Flag
    s.reg_ww                 = Wire ( Bits(1) )
    s.reg_rr                 = Wire ( Bits(1) )
    s.reg_rrw                = Wire ( Bits(1) )
    s.reg_rw                 = Wire ( Bits(1) )
    s.start_sorting          = Wire ( Bits(1) )
    s.done                   = Wire ( Bits(1) )

    # Single Mem Port State Elements
    s.STATE_IDLE             = 0
    s.STATE_DONE             = 6
    s.STATE_SOURCE           = 1

    # Two Mem Port State Elements
    s.STATE_RR               = 2
    s.STATE_DRW              = 3
    s.STATE_SRW              = 4
    s.STATE_WW               = 5

    s.state                  = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counter Incrementer
    @s.tick_rtl
    def count_inc():

      if(s.reset):
        s.counteri.next      = 0
        s.countero.next      = 0
      else:
        # increment outer loop counter
        if(s.reg_rr):
          s.countero.next    = s.countero + 1
          s.counteri.next    = 2
        # increment inner loop counter
        if(s.reg_rw or s.reg_rrw):
          s.counteri.next    = s.counteri + 1
        # reset inner loop counter in ww state
        if(s.reg_ww):
          s.counteri.next    = 0

    @s.combinational
    def output_connect():
      s.RR.value = s.reg_rrw

    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state             = s.state.out
      next_state             = s.state.out

      # Transistions out of IDLE state
      if ( curr_state == s.STATE_IDLE ):
        if ( s.xcelreq_val ):
          next_state         = s.STATE_SOURCE

      # Transition out of SOURCE state
      if ( curr_state == s.STATE_SOURCE ):
        if (s.start_sorting and s.xcelreq_rdy):
          next_state       = s.STATE_RR
        elif(s.done):
          next_state         = s.STATE_IDLE

      # Transistions out of RR state
      if ( curr_state == s.STATE_RR ):
        if( s.memreq_rdy and s.dualmemreq_rdy):
          if(s.size == 2):
            next_state       = s.STATE_WW
          else:
            next_state       = s.STATE_DRW

      # Transistions out of DRW state
      if ( curr_state == s.STATE_DRW ):
        if( s.memreq_rdy and s.memresp_rdy and
            s.dualmemreq_rdy and s.dualmemresp_rdy):
          if(s.size == 3):
            next_state       = s.STATE_WW
          else:
            next_state       = s.STATE_SRW

      # Transistions out of SRW state
      if ( curr_state == s.STATE_SRW ):
        if( s.memreq_rdy and s.memresp_rdy and
            s.dualmemreq_rdy and s.dualmemresp_rdy):
          if( s.counteri != (s.size - 1) ):
            next_state         = s.STATE_SRW
          else:
            next_state         = s.STATE_WW

      # Transistions out of WW state
      if ( curr_state == s.STATE_WW ):
        if( s.memresp_rdy and s.dualmemresp_rdy and
            s.memreq_rdy and s.dualmemreq_rdy):
          next_state           = s.STATE_DONE

      # Transistions out of DONE state
      if ( curr_state == s.STATE_DONE ):
        if (s.memresp_val and s.dualmemresp_val and
            s.xcelresp_rdy):
          if(s.countero != s.size):
            next_state       = s.STATE_RR
          else:
            next_state       = s.STATE_SOURCE

      s.state.in_.value      = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      current_state                      = s.state.out
      s.memresp_rdy.value                = 0
      s.dualmemresp_rdy.value            = 0
      s.memreq_val.value                 = 0
      s.dualmemreq_val.value             = 0
      s.xcelresp_val.value               = 0
      s.xcelreq_rdy.value                = 0

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.reg_rr.value                   = 0
        s.reg_rw.value                   = 0
        s.reg_rrw.value                  = 0
        s.reg_ww.value                   = 0
        s.counteri.value                 = 0
        s.countero.value                 = 0
        s.start_sorting.value            = 0
        s.xcelreq_rdy.value              = 1

        # when req valid, read the first value
        if(s.xcelreq_val):
          if(s.xcelreq_msgtype == XcelReqMsg.TYPE_WRITE):
            if(s.xcelreq_msgaddr == 1):
              s.base.value               = s.xcelreq_msgdata
            s.xcelresp_val.value         = 1
            s.xcelresp_msgtype.value     = XcelRespMsg.TYPE_WRITE

      # In SOURCE state
      if (current_state == s.STATE_SOURCE):
        s.xcelreq_rdy.value = s.xcelresp_rdy
        s.xcelresp_val.value             = s.xcelreq_val

        if (s.xcelreq_val):
          if (s.xcelreq_msgtype == XcelReqMsg.TYPE_WRITE):
            if (s.xcelreq_msgaddr == 0):
              s.start_sorting.value      = 1
            elif (s.xcelreq_msgaddr == 2):
              s.size.value               = s.xcelreq_msgdata
            # Send xcel response message
            s.xcelresp_msgtype.value     = XcelRespMsg.TYPE_WRITE

          elif (s.xcelreq_msgtype == XcelReqMsg.TYPE_READ):
            s.xcelresp_msgtype.value     = XcelRespMsg.TYPE_READ
            s.xcelresp_msgdata.value     = 1
            s.done.value                 = 0

      # In RR state
      elif (current_state == s.STATE_RR):
        if(s.memreq_rdy and s.dualmemreq_rdy):
          s.memreq_val.value             = 1
          s.dualmemreq_val.value         = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.memreq_msgaddr.value         = s.base + 4 * (s.counteri + 1)
          s.dualmemreq_msgtype.value     = MemReqMsg.TYPE_READ
          s.dualmemreq_msgaddr.value     = s.base + 4 * s.counteri
          s.reg_rr.value                 = 1
        else:
          s.reg_rr.value                 = 0

      # In DRW state
      elif (current_state == s.STATE_DRW):
        if(s.memreq_rdy and s.memresp_val and
           s.dualmemreq_rdy and s.dualmemresp_val):
          s.memreq_val.value             = 1
          s.dualmemreq_val.value         = 1
          s.memresp_rdy.value            = 1
          s.dualmemresp_rdy.value        = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.dualmemreq_msgtype.value     = MemReqMsg.TYPE_WRITE
          s.memreq_msgaddr.value         = s.base + 4 * s.counteri
          s.dualmemreq_msgaddr.value     = s.base + 4 * (s.counteri - 2)
          s.reg_rr.value                 = 0
          s.reg_rrw.value                = 1
        else:
          s.reg_rr.value                 = 0
          s.reg_rrw.value                = 0

      # In SRW state
      elif (current_state == s.STATE_SRW):
        if(s.memreq_rdy and s.memresp_val and
           s.dualmemreq_rdy and s.dualmemresp_val):
          s.memreq_val.value             = 1
          s.dualmemreq_val.value         = 1
          s.memresp_rdy.value            = 1
          s.dualmemresp_rdy.value        = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.dualmemreq_msgtype.value     = MemReqMsg.TYPE_WRITE
          s.memreq_msgaddr.value         = s.base + 4 * s.counteri
          s.dualmemreq_msgaddr.value     = s.base + 4 * (s.counteri - 2)
          s.reg_rrw.value                 = 0
          s.reg_rw.value                  = 1
        else:
          s.reg_rrw.value                 = 0
          s.reg_rw.value                  = 0

      # In WW state
      elif (current_state == s.STATE_WW):
        if(s.memreq_rdy and s.memresp_val and
           s.dualmemreq_rdy and s.dualmemresp_val):
          s.memreq_val.value             = 1
          s.dualmemreq_val.value         = 1
          s.memresp_rdy.value            = 1
          s.dualmemresp_rdy.value        = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_WRITE
          s.memreq_msgaddr.value         = s.base + 4 * (s.counteri - 1)
          s.dualmemreq_msgtype.value     = MemReqMsg.TYPE_WRITE
          s.dualmemreq_msgaddr.value     = s.base + 4 * (s.counteri - 2)
          s.reg_ww.value                 = 1
          s.reg_rw.value                 = 0
          s.reg_rr.value                 = 0
          if(s.size == 2):
            s.reg_rrw.value              = 1
          else:
            s.reg_rrw.value              = 0
        else:
          s.reg_rw.value                 = 0
          s.reg_ww.value                 = 0
          s.reg_rrw.value                = 0
          s.reg_rr.value                 = 0

      # In DONE state
      elif (current_state == s.STATE_DONE):
        if(s.memresp_val and s.dualmemresp_val):
          s.memresp_rdy.value            = 1
          s.dualmemresp_rdy.value        = 1
          s.reg_ww.value                 = 0
          s.reg_rrw.value                = 0
        else:
          s.reg_ww.value                 = 0
          s.reg_rrw.value                = 0
