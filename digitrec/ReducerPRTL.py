#=========================================================================
# Reducer
#=========================================================================

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEn, Mux, Adder, ZeroExtender, RegRst
from ReducerMsg    import ReducerReqMsg, ReducerRespMsg
from pclib.ifcs    import MemReqMsg, MemRespMsg

DIGIT = 10
TYPE_READ = 0
TYPE_WRITE = 1

#=========================================================================
# Reducer Datapath
#=========================================================================

class ReducerDpath (Model):

  def __init__ ( s, k = 3 ):
  
    s.req_msg_data      = InPort   (49) 
    s.req_msg_digit     = InPort   ( 4)
    s.resp_msg_data     = OutPort  (49)
    s.resp_msg_digit    = OutPort  ( 4)
  
    s.mem_req_msg_data   = OutPort (49)
 
    s.mem_resp_msg_data  = InPort  (49)
   
    # ctrl->dpath
    s.knn_reg_en     = InPort (1)
    s.max_reg_en     = InPort (1)
    s.max_sel_en     = InPort (1)
    s.sum_reg_en     = InPort (1)

    # dpath->ctrl
    s.update_knn     = OutPort(1)

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
    s.connect( s.reg_out, s.resp_msg_data )
    




#=========================================================================
# Reducer Control
#=========================================================================

class ReducerCtrl (Model):

  def __init__( s, k = 3 ):
 
    # ctrl to toplevel
    s.req_val       = InPort  (1)
    s.req_rdy       = OutPort (1)

    s.resp_val      = OutPort (1)
    s.resp_rdy      = InPort  (1)

    s.req_msg_type  = InPort  (1)    
    s.resp_msg_type = InPort  (1)    

    s.mem_req_val   = OutPort (1)
    s.mem_req_rdy   = InPort  (1)
    s.mem_req_msg_addr = OutPort (32)
    s.mem_req_type  = OutPort (3)

    s.mem_resp_val  = InPort  (1)
    s.mem_resp_rdy  = OutPort (1)

    # ctrl->dpath
    s.knn_reg_en    = OutPort (1)
    s.max_reg_en    = OutPort (1)
    s.max_sel_en    = OutPort (1)
    s.sum_reg_en    = OutPort (1)

    # dpath->ctrl
    s.update_knn    = InPort(1)
 

    s.msg_type_reg_en = Wire ( Bits(1) )


    # State element
    s.STATE_IDLE = 0
    s.STATE_INIT = 1
    s.STATE_DONE = 2

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count  = Wire ( 5 ) # max 30

    @s.tick
    def counter():
      if ( curr_state == s.STATE_INIT ):
        s.init_count.next = s.init_count + 1
      else
        s.init_count.next = 0

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
           next_state = s.STATE_DONE

      # Transition out of INIT state
      if ( curr_state == s.STATE_INIT ):
        if ( counter == k*DIGIT ):
           next_state = s.STATE_DONE 

      # Transition out of DONE state
      if ( curr_state == s.STATE_DONE ):
      #  if ( s.resp_val and s.resp_rdy ):
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
        s.msg_type_reg_en.value  = 1

      # INI state
      elif current_state == s.STATE_INIT:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
        s.msg_type_reg_en.value  = 0
        s.mem_req_val.value      = 1
        s.mem_req_msg_addr.value = init_counter * 3
        s.mem_req_msg_type.value = TYPE_WRITE
        s.mem_resp_rdy.value     = 1 
 
      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value  = 0
        s.resp_val.value = 1
        s.msg_type_reg_en.value  = 0

    
    # Register for resp msg type     
    s.Reg_msg_type = m = RegEnRst( 1 )
    s.connect_dict({
      m.en  : s.msg_type_reg_en,
      m.in_ : s.req_msg_type,
      m.out : s.resp_msg_type,
    })
 
#=========================================================================
# Reducer Model
#=========================================================================

class ReducerPRTL (Model):

  def __init__ ( s, k = 3 ):
   
    # scheduler interface
    s.req     = InValRdyBundle  ( ReducerReqMsg()  )
    s.resp    = OutValRdyBundle ( ReducerRespMsg() )

    # local memory interface
    s.mem_req  = InValRdyBundle ( MemReqMsg(  8, 32, 49 ) )
    s.mem_resp = OutValRdyBundle( MemRespMsg( 8, 49 )     )
 
    # instantiate dpath and ctrl unit
    s.dpath   = ReducerDpath()
    s.ctrl    = ReducerCtrl() 

    # connections to in/outports
    s.connect( s.req.msg.data,            s.dpath.req_msg_data  )
    s.connect( s.req.msg.digit,           s.dpath.req_msg_digit )
    s.connect( s.req.msg.type_,           s.ctrl.req_msg_type   )
    s.connect( s.req.val,                 s.ctrl.req_val        )
    s.connect( s.req.rdy,                 s.ctrl.req_rdy        )
  
    s.connect( s.dpath.mem_req_msg_data,  s.mem_req.msg.data    )
    s.connect( s.ctrl.mem_req_msg_type,   s.mem_req.msg.type_   )
    s.connect( s.ctrl.mem_req_msg_addr,   s.mem_req.msg.addr    )
    s.connect( s.ctrl.mem_req_val,        s.mem_req.val         )
    s.connect( s.ctrl.mem_req_rdy,        s.mem_req.rdy         )
  
    s.connect( s.dpath.resp_msg_data,     s.resp.msg.data       )
    s.connect( s.dpath.resp_msg_digit,    s.resp.msg.digit      )
    s.connect( s.ctrl.resp_msg_type,      s.resp.msg.type_      )
    s.connect( s.ctrl.resp_val,           s.resp.val            )
    s.connect( s.ctrl.resp_rdy,           s.resp.rdy            )

    s.connect( s.mem_resp.msg.data, s.dpath.mem_resp_msg_data   )
    s.connect( s.mem_resp.val,      s.ctrl.mem_resp_val         )
    s.connect( s.mem_resp.rdy,      s.ctrl.mem_resp_rdy         )

    # connect dpath ctrl signals
    s.connect_auto( s.dpath, s.ctrl )


  # Line Trace
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I   "
    if s.ctrl.state.out == s.ctrl.STATE_INIT:
      state_str = "INIT"
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "D   "

    return "{} ({} {} {}) {}".format( s.req, s.dpath.adder_out, s.dpath.reg_out, state_str, s.resp )
