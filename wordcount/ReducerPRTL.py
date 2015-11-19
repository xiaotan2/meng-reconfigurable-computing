#=========================================================================
# Reducer
#=========================================================================

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEn, Mux, Adder, ZeroExtender, RegRst
from ReducerMsg    import ReducerReqMsg

#=========================================================================
# Reducer Datapath
#=========================================================================

class ReducerDpath (Model):

  def __init__ ( s ):
   
    s.req_msg_data  = InPort (1)
    s.resp_msg      = OutPort(32)
    s.sel           = InPort (1)
    s.en            = InPort (1)

    # Input Mux    
    s.reg_out = Wire(32)

    s.mux = m = Mux( 32, 2)
    s.connect_dict({
      m.sel     : s.sel,
      m.in_[0]  : 0,
      m.in_[1]  : s.reg_out
    })
    

    # Output Register
    s.adder_out = Wire(32)    

    s.reg = m = RegEn( 32 )
    s.connect_dict({
      m.en      : s.en,
      m.in_     : s.adder_out,
      m.out     : s.reg_out
    })

    # Zero Extender   
    s.zext = m = ZeroExtender( 1, 32 )
    s.connect_dict({
      m.in_     : s.req_msg_data
    })

    # Adder    
    s.add = m = Adder( 32 )
    s.connect_dict({
      m.in0     : s.zext.out,
      m.in1     : s.mux.out,
      m.cin     : 0,
      m.out     : s.adder_out
    })

    # Connect to output port
    s.connect( s.reg_out, s.resp_msg )



#=========================================================================
# Reducer Control
#=========================================================================

class ReducerCtrl (Model):

  def __init__( s ):

    s.req_val       = InPort  (1)
    s.req_rdy       = OutPort (1)

    s.resp_val      = OutPort (1)
    s.resp_rdy      = InPort  (1)

    s.req_msg_type  = InPort  (1)    

    s.sel           = OutPort (1)
    s.en            = OutPort (1)

    # State element
    s.STATE_IDLE = 0
    s.STATE_CALC = 1
    s.STATE_DONE = 2

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

    # State Transition Logic
    @s.combinational
    def state_transitions():

      curr_state = s.state.out
      next_state = s.state.out
     
      # Transition out of IDLE state
      if ( curr_state == s.STATE_IDLE ):
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 0) ):
           next_state = s.STATE_CALC
        elif ( (s.req_val and s.req_rdy) and (s.req_msg_type == 1) ):
           next_state = s.STATE_DONE

      # Transition out of CALC state
      if ( curr_state == s.STATE_CALC ):
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 1) ):
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
        s.req_rdy.value  = 1
        s.resp_val.value = 0
        s.en.value       = 1
        s.sel.value      = 0

      # CALC state
      elif current_state == s.STATE_CALC:
        s.req_rdy.value  = 1
        s.resp_val.value = 0
        s.en.value       = 1
        s.sel.value      = 1

      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value  = 0
        s.resp_val.value = 1
        s.en.value       = 0
        s.sel.value      = 0

    
 
#=========================================================================
# Reducer Model
#=========================================================================

class ReducerPRTL (Model):

  def __init__ ( s ):
   
    s.req     = InValRdyBundle  ( ReducerReqMsg() )
    s.resp    = OutValRdyBundle ( Bits(32) )
 
    s.dpath   = ReducerDpath()
    s.ctrl    = ReducerCtrl() 

    s.connect( s.req.msg.data,    s.dpath.req_msg_data )
    s.connect( s.req.msg.type_,   s.ctrl.req_msg_type  )
    s.connect( s.req.val,         s.ctrl.req_val       )
    s.connect( s.req.rdy,         s.ctrl.req_rdy       )
  
    s.connect( s.dpath.resp_msg,  s.resp.msg           )
    s.connect( s.ctrl.resp_val,   s.resp.val           )
    s.connect( s.ctrl.resp_rdy,   s.resp.rdy           )

    s.connect_auto( s.dpath, s.ctrl )


  # Line Trace
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I "
    if s.ctrl.state.out == s.ctrl.STATE_CALC:
      state_str = "C "
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "D "

    return "{} ({} {} {}) {}".format( s.req, s.dpath.adder_out, s.dpath.reg_out, state_str, s.resp )
