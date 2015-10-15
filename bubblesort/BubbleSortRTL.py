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

    # Bypass queues
    s.xcelreq_queue     = SingleElementPipelinedQueue( XcelReqMsg() )
    s.memreq_queue      = SingleElementBypassQueue( MemReqMsg(8,32,32) )
    s.memresp_queue     = SingleElementBypassQueue( MemRespMsg(8,32))
    s.connect_pairs(
      s.memreq_queue.deq,  s.memreq,
      s.xcelreq_queue.enq, s.xcelreq,
      s.memresp_queue.enq, s.memresp
    )

    # Connect datapath signals
    s.connect(s.memresp_queue.deq.msg.data, s.dpath.mem_req_rdata)
    s.connect(s.dpath.mem_resp_wdata, s.memreq_queue.enq.msg.data)

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

    mux_str       = " m1{}|m2{}|m3{}|m4{}|m5{}".format(
                            s.dpath.reg_mux1_out, 
                            s.dpath.reg_mux2_out, 
                            s.dpath.reg_mux3_out, 
                            s.dpath.reg_mux4_out, 
                            s.dpath.reg_mux5_out)

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

    s.mem_req_rdata             = InPort( Bits(32) )
    s.mem_resp_wdata            = OutPort( Bits(32) )

    #--------------------------------------------------------------
    # Registers
    #--------------------------------------------------------------

    # Register first, second and write register
    s.reg_fir                   = Wire( Bits(32) ) # r1
    s.reg_sec                   = Wire( Bits(32) ) # r2

    # Flag
    s.swap                      = Wire( Bits(1) )

    # Control Signals: Control Unit -> Datapath
    s.initial                   = InPort( Bits(1) )
    s.end                       = InPort( Bits(1) )
    s.reading                   = InPort( Bits(1) )

    # Mux Output Registers
    s.reg_mux1_out              = Wire( Bits(32) )
    s.reg_mux2_out              = Wire( Bits(32) )
    s.reg_mux3_out              = Wire( Bits(32) )
    s.reg_mux4_out              = Wire( Bits(32) )
    s.reg_mux5_out              = Wire( Bits(32) )

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
      if(s.reg_mux2_out > s.reg_mux1_out):
        s.swap.value            = 1
      else:
        s.swap.value            = 0

      # Connect Output port
      s.reg_sec.value           = s.mem_req_rdata
      s.mem_resp_wdata.value    = s.reg_mux3_out

    # Instantiate Mux for choosing register2
    s.mux_1 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.end,
      m.in_[ WRITE_CYCLE ]   : s.reg_sec,
      m.in_[ READ_CYCLE ]    : s.reg_fir,
      m.out                  : s.reg_mux1_out,
    })

    # Instantiate Mux for choosing register1
    s.mux_2 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.initial,
      m.in_[ MUX_IN1 ]       : s.reg_fir,
      m.in_[ MUX_IN2 ]       : s.reg_sec,
      m.out                  : s.reg_mux2_out,
    })

    # Instantiate Mux for choosing write memory data
    s.mux_3 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.swap,
      m.in_[ MUX_IN1 ]       : s.reg_mux2_out,
      m.in_[ MUX_IN2 ]       : s.reg_mux1_out,
      m.out                  : s.reg_mux3_out,
    })

    # Instantiate Mux for choosing register1 to store
    s.mux_4 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.swap,
      m.in_[ MUX_IN1 ]       : s.reg_mux1_out,
      m.in_[ MUX_IN2 ]       : s.reg_mux2_out,
      m.out                  : s.reg_mux4_out,
    })

    s.mux_5 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.reading,
      m.in_[ MUX_IN1 ]       : s.reg_fir,
      m.in_[ MUX_IN2 ]       : s.reg_mux4_out,
      m.out                  : s.reg_mux5_out,
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

    # Control signals (ctrl -> dpath)
    s.initial                = OutPort ( Bits(1) )
    s.end                    = OutPort ( Bits(1) )
    s.reading                = OutPort ( Bits(1) )

    # Counter Signals
    s.counteri               = Wire ( Bits(COUNTER_BITS) )
    s.countero               = Wire ( Bits(COUNTER_BITS) )

    # Flag
    s.reg_initial            = Wire( Bits(1) )
    s.reg_end                = Wire ( Bits(1) )
    s.reg_reading            = Wire ( Bits(1) )
    s.start_sorting          = Wire ( Bits(1) )
    s.done                   = Wire ( Bits(1) )

    # State Elements
    s.STATE_IDLE             = 0
    s.STATE_INIT             = 1
    s.STATE_READ             = 2
    s.STATE_RW               = 3
    s.STATE_WR               = 4
    s.STATE_END              = 5
    s.STATE_DONE             = 6
    s.STATE_SOURCE           = 7

    s.state                  = RegRst( 3, reset_value = s.STATE_IDLE )

    # Counter Incrementer
    @s.tick_rtl
    def count_inc():

      if(s.reset):
        s.counteri.next      = 0
        s.countero.next      = 0
      else:
        if(s.reg_initial):
          s.countero.next    = s.countero + 1
        if(s.reg_reading):
          s.counteri.next    = s.counteri + 1
        if(s.reg_end):
          s.counteri.next    = 0

    # Output Connection
    @s.combinational
    def connector():
      s.initial.value        = s.reg_initial
      s.end.value            = s.reg_end
      s.reading.value        = s.reg_reading

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
          next_state         = s.STATE_INIT
        elif(s.done):
          next_state         = s.STATE_IDLE

      # Transistions out of INIT state
      if ( curr_state == s.STATE_INIT ):
        if( s.memreq_rdy ):
          next_state         = s.STATE_READ

      # Transistions out of READ state
      if ( curr_state == s.STATE_READ ):
        if( s.memreq_rdy and s.memresp_rdy):
          next_state         = s.STATE_WR

      # Transistions out of RW state
      if ( curr_state == s.STATE_RW ):
        if( s.memreq_rdy and s.memresp_rdy):
          next_state         = s.STATE_WR

      # Transistions out of WR state
      if ( curr_state == s.STATE_WR ):
        if ( s.memreq_rdy and s.memresp_rdy):
          if ( s.counteri != s.size ):
            next_state       = s.STATE_RW
          else:
            next_state       = s.STATE_END

      # Transistions out of END state
      if ( curr_state == s.STATE_END ):
        if (s.memreq_rdy and s.memresp_rdy ):
          next_state         = s.STATE_DONE

      # Transistions out of DONE state
      if ( curr_state == s.STATE_DONE ):
        if (s.memresp_val and s.xcelresp_rdy):
          if(s.countero != s.size):
            next_state       = s.STATE_INIT
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
      s.memreq_val.value                 = 0
      s.xcelresp_val.value               = 0
      s.xcelreq_rdy.value                = 0
      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.reg_initial.value              = 0
        s.reg_end.value                  = 0
        s.reg_reading.value              = 0
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

      # In INIT state
      elif (current_state == s.STATE_INIT):
        if(s.memreq_rdy):
          s.reg_initial.value            = 1
          s.reg_reading.value            = 1
          s.memreq_val.value             = 1
          #s.memresp_rdy.value           = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.memreq_msgaddr.value         = s.base + 4 * s.counteri

      # In READ state
      elif (current_state == s.STATE_READ):
        if(s.memreq_rdy and s.memresp_val):
          s.reg_reading.value            = 1
          s.memreq_val.value             = 1
          s.memresp_rdy.value            = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.memreq_msgaddr.value         = s.base + 4 * s.counteri
        else:
          s.reg_initial.value            = 0
          s.reg_reading.value            = 0

      # In RW state
      elif (current_state == s.STATE_RW):
        if(s.memreq_rdy and s.memresp_val):
          s.reg_reading.value            = 1
          s.memreq_val.value             = 1
          s.memresp_rdy.value            = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.memreq_msgaddr.value         = s.base + 4 * s.counteri
        else:
          s.reg_reading.value            = 0
      # In WR state
      elif (current_state == s.STATE_WR):
        if(s.memreq_rdy and s.memresp_val):
          s.reg_reading.value            = 0
          s.memreq_val.value             = 1
          s.memresp_rdy.value            = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_WRITE
          s.memreq_msgaddr.value         = s.base + 4 * (s.counteri - 2)
        else:
          s.reg_reading.value            = 0
      # In END state
      elif (current_state == s.STATE_END):
        if(s.memreq_rdy and s.memresp_val):
          s.reg_end.value                = 1
          s.memreq_val.value             = 1
          s.memresp_rdy.value            = 1
          s.memreq_msgtype.value         = MemReqMsg.TYPE_WRITE
          s.memreq_msgaddr.value         = s.base + 4 * (s.counteri - 1)
        else:
          s.reg_reading.value            = 0

      # In DONE state
      elif (current_state == s.STATE_DONE):
        if(s.memresp_val and s.xcelresp_rdy):
          s.reg_end.value                = 0
          s.memresp_rdy.value            = 1
          s.memreq_val.value             = 0
          s.memreq_msgtype.value         = MemReqMsg.TYPE_READ
          s.done.value                   = 1
        else:
          s.reg_end.value                = 0
          s.memreq_val.value             = 0

# Memory Adapter that supports both one and two mem ports for bubble sort
class BSortMemoryAdapter( Model ) :

  def __init__(s):

    s.memreq_val              = OutPort( Bits(1) )
    s.memreq_rdy              = InPort( Bits(1) )
    s.memreq_msgtype          = OutPort( Bits(3) )
    s.memreq_msgaddr          = OutPort( Bits(32) )
    s.memreq_msgdata          = OutPort( Bits(32) )

    s.memresp_val             = InPort( Bits(1) )
    s.memresp_rdy             = OutPort( Bits(1) )
    s.memresp_msgdata         = InPort( Bits(32) )
    
    s.two_mem_ports           = OutPort( Bits(1) )
