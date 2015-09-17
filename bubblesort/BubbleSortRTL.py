from pymtl        import *
from pclib.rtl    import Mux
from pclib.ifcs import XcelMsg, MemMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

# Constant

MUX_IN1 = 0
MUX_IN2 = 1
COUNTER_BITS = 8
READ_CYCLE = 1
WRITE_CYCLE = 0

class BubbleSortRTL( Model ) :

  # Constructor

  def __init__( s ):

    # Interface

    s.xcelreq        = InValRdyBundle  ( XcelReqMsg() )
    s.xcelresp       = OutValRdyBundle ( XcelReqMsg() )
    s.memreq         = OutValRdyBundle ( MemReqMsg() )
    s.memresp        = InValRdyBundle  ( MemReqMsg() )

    s.xcelreq_val  = InPort(1);
    s.xcelreq_rdy  = OutPort(1);
    s.xcelresp_val = OutPort(1);
    s.xcelresp_rdy = InPort(1);

    s.mem.reqs_val  = InPort(1);
    s.mem.reqs_rdy  = OutPort(1);
    s.mem.resps_val = OutPort(1);
    s.mem.resps_rdy = InPort(1);

    s.dpath          = BSDatapathRTL()
    s.ctrl           = BSControlUnitRTL()

    # Connect datapath signals
    s.connect(s.mem.resps.data, s.dpath.mem_req_rdata)
    s.connect(s.dpath.mem_req_add, s.mem.reqs.addr)
    s.connect(s.dpath.mem_resp_wadd, s.mem.reqs.data)
    s.connect(s.xcelreq.data, s.dpath.in_base)
    s.connect(s.xcelreq.data, s.dpath.in_size)

    # Connect control unit signals
    s.connect()

    # Connect status/control signals
    s.connect_auto( s.dpath, s.ctrl )

class BSDatapathRTL( Model ):

  def __init__(s):

    #--------------------------------------------------------------
    # Interface
    #--------------------------------------------------------------

    s.in_base                   = InPort( Bits(32) )
    s.in_size                   = InPort( Bits(32) )
    s.mem_req_rdata             = InPort( Bits(32) )
    s.mem_req_add               = OutPort( Bits(32) )
    s.mem_resp_wdata            = OutPort( Bits(32) )

    #--------------------------------------------------------------
    # Registers
    #--------------------------------------------------------------

    # Register first, second and write register
    s.reg_fir                   = Wire( Bits(32) ) # r1
    s.reg_sec                   = Wire( Bits(32) ) # r2
    s.reg_wr                    = Wire( Bits(32) )
    s.reg_base                  = Wire( Bits(32) )
    s.reg_size                  = Wire( Bits(32) )

    # Flag
    s.swap                      = Wire( Bits(1) )

    # Control Signals: Control Unit -> Datapath
    s.initial                   = InPort( Bits(1) )
    s.end                       = InPort( Bits(1) )
    s.done                      = InPort( Bits(1) )
    s.rw                        = InPort( Bits(1) )
    s.r_base                    = InPort( Bits(1) )
    s.r_size                    = InPort( Bits(1) )

    # Control Signals: Datapath -> Control Unit
    s.counteri                  = OutPort( Bits(COUNTER_BITS) )
    s.countero                  = OutPort( Bits(COUNTER_BITS) )

    # Counter Registers
    s.reg_counteri              = Wire( Bits(COUNTER_BITS) )
    s.reg_countero              = Wire( Bits(COUNTER_BITS) )
    s.reg_counteri_base         = Wire( Bits(32) )
    s.reg_counteri_base_de      = Wire( Bits(32) )
    s.reg_counteri_base_dt      = Wire( Bits(32) )
    s.reg_counteri_in           = Wire( Bits(COUNTER_BITS) )
    s.reg_countero_in           = Wire( Bits(COUNTER_BITS) )

    # Mux Output Registers
    s.reg_mux1_out              = Wire( Bits(32) )
    s.reg_mux2_out              = Wire( Bits(32) )
    s.reg_mux3_out              = Wire( Bits(32) )
    s.reg_mux4_out              = Wire( Bits(32) )
    s.reg_mux5_out              = Wire( Bits(32) )
    s.reg_mux6_out              = Wire( Bits(32) )
    s.reg_mux7_out              = Wire( Bits(32) )
    s.reg_mux8_out              = Wire( Bits(32) )
    s.reg_mux9_out              = Wire( Bits(32) )
    s.reg_mux10_out             = Wire( Bits(32) )
    s.reg_mux11_out             = Wire( Bits(32) )
    s.reg_mux12_out             = Wire( Bits(32) )
    s.reg_mux13_out             = Wire( Bits(32) )
    s.reg_mux14_out             = Wire( Bits(32) )

    #--------------------------------------------------------------
    # Ticking Concurrent Blocks
    #--------------------------------------------------------------

    @s.tick_rtl
    def updateRegister():
      if s.reset:
        s.reg_sec.next = 0
        s.reg_fir.next = 0
        s.reg_base.next = 0
        s.reg_size.next = 0
        s.reg_wr.next = 0
      else:
        s.reg_sec.next = s.reg_mux1_out
        s.reg_fir.next = s.reg_mux5_out
        s.reg_base.next = s.reg_mux12_out
        s.reg_size.next = s.reg_mux13_out
        s.reg_wr.next = s.reg_mux9_out

    @s.tick_rtl
    def updateCounter():
      if s.reset:
        s.reg_counteri.next = 0
        s.reg_countero.next = 0
      else:
        s.reg_counteri.next = s.reg_mux10_out
        s.reg_countero.next = s.reg_mux8_out
      s.reg_counteri_base.next = sext(s.counteri, 32) + s.in_base
      s.reg_counteri_base_de.next = s.reg_counteri_base - 1
      s.reg_counteri_base_dt.next = s.reg_counteri_base - 2
      s.reg_counteri_in.next = s.reg_counteri + 1
      s.reg_countero_in.next = s.reg_countero + 1

    #--------------------------------------------------------------
    # Combinational Logic
    #--------------------------------------------------------------

    @s.combinational
    def comb_logic():
      # Comparator
      if(s.reg_mux2_out > s.reg_sec):
        s.swap.value = 1
      else:
        s.swap.value = 0
      # Connect Output port
      s.counteri.value = s.reg_counteri
      s.countero.value = s.reg_countero
      s.mem_req_add.value = s.reg_mux14_out

    # Instantiate Mux for choosing register2
    s.mux_1 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.rw,
      m.in_[ WRITE_CYCLE ]   : s.reg_sec,
      m.in_[ READ_CYCLE ]    : s.mem_read_data,
      m.out                  : s.reg_mux1_out,
    })

    # Instantiate Mux for choosing register1
    s.mux_2 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.initial,
      m.in_[ MUX_IN1 ]   : s.reg_fir,
      m.in_[ MUX_IN2 ]   : s.reg_sec,
      m.out              : s.reg_mux2_out,
    })

    # Instantiate Mux for choosing write memory data
    s.mux_3 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.swap,
      m.in_[ MUX_IN1 ]   : s.reg_mux2_out,
      m.in_[ MUX_IN2 ]   : s.reg_sec,
      m.out              : s.reg_mux3_out,
    })

    # Instantiate Mux for choosing register1 to store
    s.mux_4 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.swap,
      m.in_[ MUX_IN1 ]   : s.reg_sec,
      m.in_[ MUX_IN2 ]   : s.reg_mux2_out,
      m.out              : s.reg_mux4_out,
    })

    # Instantiate Mux for choosing memory write address
    s.mux_5 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.rw,
      m.in_[ WRITE_CYCLE ]   : s.reg_fir,
      m.in_[ READ_CYCLE ]    : s.reg_mux4_out,
      m.out                  : s.reg_mux5_out,
    })

    # Instantiate Mux for choosing memory read address
    s.mux_6 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.end,
      m.in_[ MUX_IN1 ]   : s.reg_counteri_base_dt,
      m.in_[ MUX_IN2 ]   : s.reg_counteri_base_de,
      m.out              : s.reg_mux6_out,
    })

    # Instantiate Mux for choosing inner loop counter
    s.mux_7 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.end,
      m.in_[ MUX_IN1 ]   : s.reg_counteri_in,
      m.in_[ MUX_IN2 ]   : 0,
      m.out              : s.reg_mux7_out,
    })

    # Instantiate Mux for choosing outer loop counter
    s.mux_8 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.done,
      m.in_[ MUX_IN1 ]   : s.reg_mux11_out,
      m.in_[ MUX_IN2 ]   : 0,
      m.out              : s.reg_mux8_out,
    })

    # Instantiate Mux for choosing outer loop counter
    s.mux_9 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.rw,
      m.in_[ WRITE_CYCLE ]   : s.reg_wr,
      m.in_[ READ_CYCLE ]    : s.reg_mux3_out,
      m.out                  : s.reg_mux9_out,
    })

    # Instantiate Mux for choosing outer loop counter
    s.mux_10 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.rw,
      m.in_[ WRITE_CYCLE ]   : s.reg_counteri,
      m.in_[ READ_CYCLE ]    : s.reg_mux7_out,
      m.out                  : s.reg_mux10_out,
    })


    # Instantiate Mux for choosing outer loop counter
    s.mux_11 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.initial,
      m.in_[ MUX_IN1 ]   : s.reg_countero,
      m.in_[ MUX_IN2 ]   : s.reg_countero_in,
      m.out              : s.reg_mux11_out,
    })


    # Instantiate Mux for choosing outer loop counter
    s.mux_12 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.r_base,
      m.in_[ MUX_IN1 ]   : s.reg_base,
      m.in_[ MUX_IN2 ]   : s.in_base,
      m.out              : s.reg_mux12_out,
    })

    # Instantiate Mux for choosing outer loop counter
    s.mux_13 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel              : s.r_size,
      m.in_[ MUX_IN1 ]   : s.reg_size,
      m.in_[ MUX_IN2 ]   : s.in_size,
      m.out              : s.reg_mux13_out,
    })

    # Instantiate Mux for choosing outer loop counter
    s.mux_14 = m = Mux( 32, 2 )
    s.connect_dict({
      m.sel                  : s.rw,
      m.in_[ WRITE_CYCLE ]   : s.reg_mux6_out,
      m.in_[ READ_CYCLE ]    : s.reg_counteri_base,
      m.out                  : s.reg_mux14_out,
    })

class BSControlUnitRTL( Model ) :

  # Constructor

  def __init__( s ):

    # Interface
    s.size             = InPort  ( Bits(32) )

    s.xcelreq_val  = InPort(1);
    s.xcelreq_rdy  = OutPort(1);
    s.xcelresp_val = OutPort(1);
    s.xcelresp_rdy = InPort(1);

    s.mem.reqs_val  = InPort(1);
    s.mem.reqs_rdy  = OutPort(1);
    s.mem.resps_val = OutPort(1);
    s.mem.resps_rdy = InPort(1);

    # Control signals (ctrl -> dpath)
    s.initial          = OutPort ( Bits(1) )
    s.end              = OutPort ( Bits(1) )
    s.done             = OutPort ( Bits(1) )
    s.rw               = OutPort( Bits(1) )
    s.r_base           = OutPort( Bits(1) )
    s.r_size           = OutPort( Bits(1) )

    # Control signal (dpath -> ctrl)
    s.counteri       = InPort ( Bits(COUNTER_BITS) )
    s.countero       = InPort ( Bits(COUNTER_BITS) )

    # State Elements
    s.STATE_IDLE       = 0
    s.STATE_BASE       = 1
    s.STATE_SIZE       = 2
    s.STATE_READ       = 3
    s.STATE_INIT       = 4
    s.STATE_WRITE      = 5
    s.STATE_END        = 6
    s.STATE_DONE       = 7

    s.state            = RegRst( 3, reset_value = s.STATE_IDLE )

    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state        = s.state.out
      next_state        = s.state.out

      # Transistions out of IDLE state
      if ( curr_state == s.STATE_IDLE ):
        if ( s.xcelreq_val ):
          next_state    = s.STATE_BASE

      # Transistions out of BASE state
      if ( curr_state == s.STATE_BASE ):
        if( s.xcelreq_val ):
          next_state    = s.STATE_SIZE

      # Transistions out of SIZE state
      if ( curr_state == s.STATE_SIZE ):
        next_state    = s.STATE_READ

      # Transistions out of READ state
      if ( curr_state == s.STATE_READ ):
        if ( s.mem.resps_val && s.mem.reqs_rdy ):
          if ( s.counteri == 0 ):
            next_state    = s.STATE_INIT
          else:
            next_state    = s.STATE_WRITE
        else:
          next_state    = s.STATE_READ

      # Transistions out of INITIAL state
      if ( curr_state == s.STATE_INIT ):
        if ( s.mem.resps_val && s.mem.reqs_rdy):
          next_state    = s.STATE_WRITE

      # Transistions out of WRITE state
      if ( curr_state == s.STATE_WRITE ):
        if (s.mem.resps_val && s.mem.reqs_rdy ):
          if ( s.counteri == s.size ):
            next_state    = s.STATE_END
          else:
            next_state    = s.STATE_READ
        else:
          next_state    = s.STATE_WRITE

      # Transistions out of END state
      if ( curr_state == s.STATE_END ):
        if (s.mem.resps_val && s.mem.reqs_rdy ):
          if (s.countero == s.size):
            next_state    = s.STATE_DONE
          else:
            next_state    = s.STATE_READ
        else:
          next_state      = s.STATE_END

      # Transistions out of DONE state
      if ( curr_state == s.STATE_DONE ):
        if(s.xcelresps_rdy)
          next_state    = s.STATE_IDLE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      current_state = s.state.out

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 0
        s.r_base.value             = 0
        s.r_size.value             = 0

      # In BASE state
      elif (current_state == s.STATE_BASE):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 0
        s.r_base.value             = 1
        s.r_size.value             = 0
        s.xcelreq_rdy              = 1

      # In SIZE state
      elif (current_state == s.STATE_SIZE):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 0
        s.r_base.value             = 0
        s.r_size.value             = 1
        s.xcelreq_rdy              = 1

      # In READ state
      elif (current_state == s.STATE_READ):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 1
        s.r_base.value             = 0
        s.r_size.value             = 0
        s.mem.resps_rdy            = 1
        s.mem.req_val              = 1

      # In INIT state
      elif (current_state == s.STATE_INIT):
        s.initial.value            = 1
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 1
        s.r_base.value             = 0
        s.r_size.value             = 0
        s.mem.resps_rdy            = 1
        s.mem.req_val              = 1

      # In WRITE state
      elif (current_state == s.STATE_WRITE):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 0
        s.rw.value                 = 0
        s.r_base.value             = 0
        s.r_size.value             = 0
        s.mem.resps_rdy            = 1
        s.mem.req_val              = 1

      # In END state
      elif (current_state == s.STATE_END):
        s.initial.value            = 0
        s.end.value                = 1
        s.done.value               = 0
        s.rw.value                 = 0
        s.r_base.value             = 0
        s.r_size.value             = 0
        s.mem.resps_rdy            = 1
        s.mem.req_val              = 1

      # In DONE state
      elif (current_state == s.STATE_DONE):
        s.initial.value            = 0
        s.end.value                = 0
        s.done.value               = 1
        s.rw.value                 = 0
        s.r_base.value             = 0
        s.r_size.value             = 0
        s.xcelresps_val            = 0