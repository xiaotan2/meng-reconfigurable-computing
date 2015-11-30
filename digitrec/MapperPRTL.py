#=========================================================================
# Mapper
#=========================================================================

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEn, Mux, Adder, ZeroExtender, RegRst, Reg, EqComparator
from MapperMsg     import MapperReqMsg, MapperRespMsg

DATA_NBITS     = 49
DIGIT_NBITS    = 4
TYPE_NBITS     = 1
DISTANCE_NBITS = 6

#=========================================================================
# Mapper Datapath
#=========================================================================

class MapperDpath (Model):

  def __init__ ( s ):

    # Interface   
    s.req_msg_data   = InPort  (DATA_NBITS)
    s.resp_msg_data  = OutPort (DISTANCE_NBITS)
    s.req_msg_type   = InPort  (TYPE_NBITS)
    s.resp_msg_type  = OutPort (TYPE_NBITS)
    s.req_msg_digit  = InPort  (DIGIT_NBITS)
    s.resp_msg_digit = OutPort (DIGIT_NBITS)

    # Control signals (ctrl -> dpath)
    s.en_test        = InPort  (1)
    s.en_train       = InPort  (1)
    s.en_out         = InPort  (1)
    s.sel_out        = InPort  (1)
    s.sel            = InPort  (6)


    # Input Mux for Test Data
    s.in_test = Wire(DATA_NBITS) 
    s.mux_in_test = m = Mux( DATA_NBITS, 2 )
    s.connect_dict({
      m.sel     : s.req_msg_type,
      m.in_[0]  : s.in_test,
      m.in_[1]  : s.req_msg_data,
      m.out     : s.in_test
    })

    # Input Mux for Train Data
    s.in_train = Wire(DATA_NBITS)
    s.mux_in_train = m = Mux( DATA_NBITS, 2 )
    s.connect_dict({
      m.sel     : s.req_msg_type,
      m.in_[0]  : s.req_msg_data,
      m.in_[1]  : s.in_train,
      m.out     : s.in_train
    })

    # Register for Test Data 
    s.out_test = Wire(DATA_NBITS)    
    s.reg_test = m = RegEn( DATA_NBITS )
    s.connect_dict({
      m.en      : s.en_test,
      m.in_     : s.in_test,
      m.out     : s.out_test
    })

    # Register for Train Data 
    s.out_train = Wire(DATA_NBITS)    
    s.reg_train = m = RegEn( DATA_NBITS )
    s.connect_dict({
      m.en      : s.en_train,
      m.in_     : s.in_train,
      m.out     : s.out_train
    })

    # 49-1 Mux for Test Data
    s.data_test = Wire(1) 
    s.mux_test = m = Mux( 1, 49 )
    for i in range(49):
      s.connect( m.in_[i], s.out_test[i] )
    s.connect( m.sel, s.sel )
    s.connect( m.out, s.data_test )

    # 49-1 Mux for Train Data
    s.data_train = Wire(1) 
    s.mux_train = m = Mux( 1, 49 )
    for i in range(49):
      s.connect( m.in_[i], s.out_train[i] )
    s.connect( m.sel, s.sel )
    s.connect( m.out, s.data_train )

    # Comparator
    s.is_not_equal = Wire(1)
    s.is_equal = Wire(1)
    s.comp = m = EqComparator( 1 )
    s.connect_dict({
      m.in0     : s.data_test,
      m.in1     : s.data_train,
      m.out     : s.is_equal
    })
    @s.combinational
    def not_value():
      s.is_not_equal.value = ~s.is_equal 
   
    # Zero Extender   
    s.zext = m = ZeroExtender( 1, DISTANCE_NBITS )
    s.connect_dict({
      m.in_     : s.is_not_equal
    })

    # Input Mux for Adder
    s.reg_out = Wire(DISTANCE_NBITS)
    s.mux_add = m = Mux( DISTANCE_NBITS, 2 )
    s.connect_dict({
      m.sel     : s.sel_out,
      m.in_[0]  : 0,
      m.in_[1]  : s.reg_out
    })

    # Adder    
    s.add = m = Adder( DISTANCE_NBITS )
    s.connect_dict({
      m.in0     : s.zext.out,
      m.in1     : s.mux_add.out,
      m.cin     : 0
    })

    # Output Register
    s.reg = m = RegEn( DISTANCE_NBITS )
    s.connect_dict({
      m.en      : s.en_out,
      m.in_     : s.add.out,
      m.out     : s.reg_out
    })
   

    # Connect to output port
    s.connect( s.reg_out,       s.resp_msg_data  )
    s.connect( 0,               s.resp_msg_type  )
    s.connect( s.req_msg_digit, s.resp_msg_digit )


#=========================================================================
# Mapper Control
#=========================================================================

class MapperCtrl (Model):

  def __init__( s ):

    s.req_val       = InPort  (1)
    s.req_rdy       = OutPort (1)

    s.resp_val      = OutPort (1)
    s.resp_rdy      = InPort  (1)
     
    s.req_msg_type  = InPort  (1)

    # Control signals (ctrl -> dpath)
    s.en_test        = OutPort  (1)
    s.en_train       = OutPort  (1)
    s.en_out         = OutPort  (1)
    s.sel_out        = OutPort  (1)
    s.sel            = OutPort  (6)


    # State element
    s.STATE_IDLE = 0
    s.STATE_INIT = 1
    s.STATE_CALC = 2
    s.STATE_DONE = 3

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

    s.counter = Reg( DATA_NBITS )


    # State Transition Logic
    @s.combinational
    def state_transitions():

      curr_state = s.state.out
      next_state = s.state.out
     
      # Transition out of IDLE state
      if ( curr_state == s.STATE_IDLE ):
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 1) ):
           next_state = s.STATE_INIT
        elif ( (s.req_val and s.req_rdy) and (s.req_msg_type == 0) ):
           next_state = s.STATE_CALC
        
      # Transition out of INIT state
      if ( curr_state == s.STATE_INIT ):
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 0) ):
           next_state = s.STATE_CALC

      # Transition out of CALC state
      if ( curr_state == s.STATE_CALC ):
        if ( (s.counter.out + 1) == DATA_NBITS ):
           next_state = s.STATE_DONE 

      # Transition out of DONE state
      if ( curr_state == s.STATE_DONE ):
        if ( s.resp_val and s.resp_rdy ):
           next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    # State Output Logic
    @s.combinational
    def state_outputs():
   
      current_state = s.state.out

      # IDLE state
      if current_state == s.STATE_IDLE:
        s.req_rdy.value     = 1
        s.resp_val.value    = 0
        s.en_out.value      = 0
        s.en_test.value     = 1
        s.en_train.value    = 1
        s.sel.value         = 0
        s.sel_out.value     = 0
        s.counter.in_.value = 0
        
      # INIT state
      elif current_state == s.STATE_INIT:
        s.req_rdy.value     = 1
        s.resp_val.value    = 0
        s.en_out.value      = 0
        s.en_test.value     = 0
        s.en_train.value    = 1
        s.sel.value         = 0
        s.sel_out.value     = 0
        s.counter.in_.value = 0
        
      # CALC state
      elif current_state == s.STATE_CALC:
        s.req_rdy.value     = 0
        s.resp_val.value    = 0
        s.en_out.value      = 1
        if ( s.counter.out == 0 ):
          s.sel_out.value   = 0
        else:
          s.sel_out.value   = 1
        s.en_test.value     = 0
        s.en_train.value    = 0
        s.sel.value         = s.counter.out
        s.counter.in_.value = s.counter.out + 1

      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value     = 0
        s.resp_val.value    = 1
        s.en_out.value      = 0
        s.en_test.value     = 0
        s.en_train.value    = 0
        s.sel.value         = 0
        s.sel_out.value     = 0
        s.counter.in_.value = 0

    
#=========================================================================
# Mapper Model
#=========================================================================

class MapperPRTL (Model):

  def __init__ ( s ):
   
    s.req     = InValRdyBundle  ( MapperReqMsg()  )
    s.resp    = OutValRdyBundle ( MapperRespMsg() )
 
    s.dpath   = MapperDpath()
    s.ctrl    = MapperCtrl() 

    s.connect( s.req.msg.data,        s.dpath.req_msg_data  )
    s.connect( s.req.msg.digit,       s.dpath.req_msg_digit )
    s.connect( s.req.msg.type_,       s.dpath.req_msg_type  )
    s.connect( s.req.msg.type_,       s.ctrl.req_msg_type   )
    s.connect( s.req.val,             s.ctrl.req_val        )
    s.connect( s.req.rdy,             s.ctrl.req_rdy        )
  
    s.connect( s.dpath.resp_msg_data,  s.resp.msg.data      )
    s.connect( s.dpath.resp_msg_digit, s.resp.msg.digit     )
    s.connect( s.dpath.resp_msg_type,  s.resp.msg.type_     )
    s.connect( s.ctrl.resp_val,        s.resp.val           )
    s.connect( s.ctrl.resp_rdy,        s.resp.rdy           )

    s.connect_auto( s.dpath, s.ctrl )


  # Line Trace
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "ID "
    if s.ctrl.state.out == s.ctrl.STATE_INIT:
      state_str = "IN "
    if s.ctrl.state.out == s.ctrl.STATE_CALC:
      state_str = "CA "
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "DO "

    return "{} ({} {} {} {} {} {} {}) {}".format( s.req, s.dpath.sel, s.dpath.data_test, s.dpath.data_train, s.dpath.is_not_equal, s.dpath.add.out, s.dpath.reg_out, state_str, s.resp )
