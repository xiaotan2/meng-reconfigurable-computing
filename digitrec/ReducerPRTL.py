#=========================================================================
# Reducer
#=========================================================================

import math

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEnRst, Mux, Adder, ZeroExtender, RegRst, RegisterFile
from ReducerMsg    import ReducerReqMsg, ReducerRespMsg

DIGIT         = 10
TYPE_READ     = 0
TYPE_WRITE    = 1
RE_DATA_SIZE  = 6
#=========================================================================
# Reducer Datapath
#=========================================================================

class ReducerDpath (Model):

  def __init__ ( s, k = 3 ):
  
    s.req_msg_data      = InPort   (RE_DATA_SIZE) 
    s.req_msg_digit     = InPort   (4)
    s.resp_msg_data     = OutPort  (RE_DATA_SIZE)
    s.resp_msg_digit    = OutPort  (4)
  
    # ctrl->dpath
    s.knn_reg_en     = InPort (1)
    s.max_reg_en     = InPort (1)
    s.max_mux_sel    = InPort (1)
    s.sum_reg_en     = InPort (1)
    s.knn_wr_addr    = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr    = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    # dpath->ctrl
    s.knn_update     = OutPort(1)

    # internal wires
    s.knn_rd_data    = Wire( Bits( RE_DATA_SIZE ) )
    s.knn_wr_data    = Wire( Bits( RE_DATA_SIZE ) )
    
#    @s.combinational
#    def combination_logic():
#      s.knn_wr_data.value = 50

    # register file
    s.knn_table = m = RegisterFile( dtype=Bits(RE_DATA_SIZE), 
                      nregs=k*DIGIT, rd_ports=1, wr_ports=1, const_zero=False ) 
    s.connect_dict({
      m.rd_addr[0] : s.knn_rd_addr,
      m.rd_data[0] : s.knn_rd_data,
      m.wr_addr    : s.knn_wr_addr,
      m.wr_data    : 50,
      m.wr_en      : s.knn_update
    })
#    # Input Mux    
#    s.reg_out = Wire(32)
#
#    s.mux = m = Mux( 32, 2)
#    s.connect_dict({
#      m.sel     : s.sel,
#      m.in_[0]  : 0,
#      m.in_[1]  : s.reg_out
#    })
#    
#
#    # Output Register
#    s.adder_out = Wire(32)    
#
#    s.reg = m = RegEn( 32 )
#    s.connect_dict({
#      m.en      : s.en,
#      m.in_     : s.adder_out,
#      m.out     : s.reg_out
#    })
#
#    # Zero Extender   
#    s.zext = m = ZeroExtender( 1, 32 )
#    s.connect_dict({
#      m.in_     : s.req_msg_data
#    })
#
#    # Adder    
#    s.add = m = Adder( 32 )
#    s.connect_dict({
#      m.in0     : s.zext.out,
#      m.in1     : s.mux.out,
#      m.cin     : 0,
#      m.out     : s.adder_out
#    })
#
#    # Connect to output port
#    s.connect( s.reg_out, s.resp_msg_data )
    




#=========================================================================
# Reducer Control
#=========================================================================

class ReducerCtrl (Model):

  def __init__( s, k = 3 ):
 
    # ctrl to toplevel
    s.req_val           = InPort  (1)
    s.req_rdy           = OutPort (1)

    s.resp_val          = OutPort (1)
    s.resp_rdy          = InPort  (1)

    s.req_msg_type      = InPort  (1)    
    s.resp_msg_type     = OutPort (1)    

    # ctrl->dpath
    s.knn_reg_en        = OutPort (1)
    s.max_reg_en        = OutPort (1)
    s.max_mux_sel       = OutPort (1)
    s.sum_reg_en        = OutPort (1)
    s.knn_wr_addr       = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr       = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30

    # dpath->ctrl
    s.knn_update        = InPort(1)
 

    s.msg_type_reg_en   = Wire ( Bits(1) )
    s.init_go           = Wire ( Bits(1) )

    # State element
    s.STATE_IDLE = 0
    s.STATE_INIT = 1
    s.STATE_DONE = 2

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count  = Wire ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30

    @s.tick
    def counter():
      if ( s.init_go == 1 ):
        s.init_count.next = s.init_count + 1
      else:
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
        if ( s.init_count == k*DIGIT - 1 ):
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
        s.req_rdy.value          = 1
        s.resp_val.value         = 0
       
        s.msg_type_reg_en.value  = 1
       
        s.init_go.value          = 0
        s.knn_update.value       = 0 

      # INI state
      elif current_state == s.STATE_INIT:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
       
        s.msg_type_reg_en.value  = 0
       
        s.init_go.value          = 1
      
        s.knn_wr_addr.value      = s.init_count
        if s.init_count == 0:
          s.knn_rd_addr.value    = 0
        else:
          s.knn_rd_addr.value      = s.init_count - 1
        s.knn_update.value       = 1 
 
      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value          = 0
        s.resp_val.value         = 1
      
        s.msg_type_reg_en.value  = 0
      
        s.init_go.value          = 0
        s.knn_update.value       = 0
    
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

    # instantiate dpath and ctrl unit
    s.dpath   = ReducerDpath()
    s.ctrl    = ReducerCtrl() 

    # connections to in/outports
    s.connect( s.req.msg.data,            s.dpath.req_msg_data  )
    s.connect( s.req.msg.digit,           s.dpath.req_msg_digit )
    s.connect( s.req.msg.type_,           s.ctrl.req_msg_type   )
    s.connect( s.req.val,                 s.ctrl.req_val        )
    s.connect( s.req.rdy,                 s.ctrl.req_rdy        )
  
    s.connect( s.dpath.resp_msg_data,     s.resp.msg.data       )
    s.connect( s.dpath.resp_msg_digit,    s.resp.msg.digit      )
    s.connect( s.ctrl.resp_msg_type,      s.resp.msg.type_      )
    s.connect( s.ctrl.resp_val,           s.resp.val            )
    s.connect( s.ctrl.resp_rdy,           s.resp.rdy            )

    # connect dpath ctrl signals
    s.connect_auto( s.dpath, s.ctrl )


  # Line Trace
  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "IDLE"
    if s.ctrl.state.out == s.ctrl.STATE_INIT:
      state_str = "INIT"
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "DONE"

    return "{} (count{} wr_data{} addr{} wr_en{} rd_dat{} {}) {}".format( s.req, s.ctrl.init_count, s.dpath.knn_wr_data, s.ctrl.knn_wr_addr, s.dpath.knn_update, s.dpath.knn_rd_data, state_str, s.resp )