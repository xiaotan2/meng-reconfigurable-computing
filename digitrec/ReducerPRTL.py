#=========================================================================
# Reducer
#=========================================================================

import math

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEnRst, Mux, Adder, ZeroExtender, RegRst, RegisterFile

from ReducerMsg    import ReducerReqMsg, ReducerRespMsg

from FindMaxPRTL   import FindMaxPRTL
from FindMaxMsg    import FindMaxReqMsg, FindMaxRespMsg
from FindMinPRTL   import FindMinPRTL
from FindMinMsg    import FindMinReqMsg, FindMinRespMsg

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
    s.resp_msg_digit    = OutPort  (4)
  
    # ctrl->dpath
    s.sum_reg_en        = InPort (1)
    s.knn_wr_addr       = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr       = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_wr_en         = InPort (1)
    
    s.FindMax_req_val   = InPort (1) 
    s.FindMax_resp_rdy  = InPort (1)

    # dpath->ctrl
    s.FindMax_req_rdy   = OutPort(1)
    s.FindMax_resp_val  = OutPort(1)


    # internal wires   
    s.knn_rd_data       = Wire( Bits( RE_DATA_SIZE ) )
    s.knn_wr_data       = Wire( Bits( RE_DATA_SIZE ) )

    s.FindMax_req_data  = Wire( Bits( RE_DATA_SIZE)  )
    s.FindMax_resp_data = Wire( Bits( RE_DATA_SIZE)  )
    s.FindMax_resp_idx  = Wire( int( math.ceil( math.log( k, 2) ) ) ) # max 10
    
    # register file
    s.knn_table = m = RegisterFile( dtype=Bits(RE_DATA_SIZE), 
                      nregs=k*DIGIT, rd_ports=1, wr_ports=1, const_zero=False ) 
    s.connect_dict({
      m.rd_addr[0] : s.knn_rd_addr,
      m.rd_data[0] : s.knn_rd_data,
      m.wr_addr    : s.knn_wr_addr,
      m.wr_data    : 50, #s.knn_wr_data,
      m.wr_en      : s.knn_wr_en
    })


    # Find max value of knn_table for a given digit
    s.connect_wire( s.knn_rd_data, s.FindMax_req_data )

    s.findmax   = m = FindMaxPRTL( RE_DATA_SIZE, k )

    s.connect_dict({
      m.req.val       : s.FindMax_req_val,        
      m.req.rdy       : s.FindMax_req_rdy,
      m.req.msg.data  : s.FindMax_req_data,
      m.resp.val      : s.FindMax_resp_val,
      m.resp.rdy      : s.FindMax_resp_rdy,
      m.resp.msg.data : s.FindMax_resp_data,
      m.resp.msg.idx  : s.FindMax_resp_idx
    })
      
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

    s.req_msg_digit     = InPort   (4)

    s.req_msg_type      = InPort  (2)    
    s.resp_msg_type     = OutPort (2)    

    # ctrl->dpath
    s.sum_reg_en        = OutPort (1)
    s.knn_wr_addr       = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr       = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_wr_en         = OutPort (1)

    s.FindMax_req_val   = OutPort (1) 
    s.FindMax_resp_rdy  = OutPort (1)

    # dpath->ctrl
    s.FindMax_req_rdy   = InPort  (1)
    s.FindMax_resp_val  = InPort  (1)

    s.msg_type_reg_en   = Wire ( Bits(1) )
    s.init_go           = Wire ( Bits(1) )
    s.max_go            = Wire ( Bits(1) )

    # State element
    s.STATE_IDLE = 0
    s.STATE_INIT = 1
    s.STATE_MAX  = 2
    s.STATE_DONE = 3

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count  = Wire ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_count   = Wire ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30

    @s.tick
    def counter():
      if ( s.init_go == 1 ):
        s.init_count.next = s.init_count + 1
      else:
        s.init_count.next = 0

      if ( s.max_go == 1 ):
        s.knn_count.next  = s.knn_count  + 1
      else:
        s.knn_count.next  = s.req_msg_digit * k

    # State Transition Logic
    @s.combinational
    def state_transitions():

      curr_state = s.state.out
      next_state = s.state.out
     
      # Transition out of IDLE state
      if ( curr_state == s.STATE_IDLE ):
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 1) ):
           next_state = s.STATE_INIT
        elif ( (s.req_val and s.req_rdy) and (s.req_msg_type == 0)
                  and (s.FindMax_req_val and s.FindMax_req_rdy) ):
           next_state = s.STATE_MAX

      # Transition out of INIT state
      if ( curr_state == s.STATE_INIT ):
        if ( s.init_count == k*DIGIT - 1 ):
           next_state = s.STATE_DONE 

      # Transition out of MAX  state
      if ( curr_state == s.STATE_MAX  ):
        if ( s.FindMax_resp_val and s.FindMax_resp_rdy ):
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

        s.knn_wr_en.value        = 0
        s.knn_wr_addr.value      = 0
        if ( (s.req_val and s.req_rdy) and (s.req_msg_type == 0) ):
          s.max_go.value           = 1
          s.FindMax_req_val.value  = 1 
          s.FindMax_resp_rdy.value = 0
          s.knn_rd_addr.value      = s.knn_count
        else:
          s.FindMax_req_val.value  = 0 
          s.FindMax_resp_rdy.value = 0
          s.knn_rd_addr.value      = 0
          s.max_go.value           = 0
         

      # INI state
      elif current_state == s.STATE_INIT:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
       
        s.msg_type_reg_en.value  = 0
       
        s.init_go.value          = 1
        s.max_go.value           = 0
      
        s.knn_wr_en.value        = 1
        s.knn_wr_addr.value      = s.init_count
        s.FindMax_req_val.value  = 0 
        s.FindMax_resp_rdy.value = 0
        # knn_rd for debugging 
        if s.init_count == 0:
          s.knn_rd_addr.value    = 0
        else:
          s.knn_rd_addr.value    = s.init_count - 1

      # MAX state
      elif current_state == s.STATE_MAX:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
       
        s.msg_type_reg_en.value  = 0
       
        s.init_go.value          = 0
        s.max_go.value           = 1
      
        s.knn_wr_en.value        = 0
        s.knn_wr_addr.value      = 0
        s.FindMax_req_val.value  = 1 
        s.FindMax_resp_rdy.value = 1
        if ( s.knn_count > k*DIGIT-1 ):
          s.knn_rd_addr.value    = 0
        else:
          s.knn_rd_addr.value    = s.knn_count

      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value          = 0
        s.resp_val.value         = 1
      
        s.msg_type_reg_en.value  = 0
      
        s.init_go.value          = 0
        s.max_go.value           = 0
    
        s.knn_wr_en.value        = 0
        s.knn_wr_addr.value      = 0
        s.FindMax_req_val.value  = 0 
        s.FindMax_resp_rdy.value = 0
        s.knn_rd_addr.value      = 0x1d

    # Register for resp msg type     
    s.Reg_msg_type = m = RegEnRst( 2 )
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
    s.connect( s.req.msg.digit,           s.ctrl.req_msg_digit  )
    s.connect( s.req.msg.type_,           s.ctrl.req_msg_type   )
    s.connect( s.req.val,                 s.ctrl.req_val        )
    s.connect( s.req.rdy,                 s.ctrl.req_rdy        )
  
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
    if s.ctrl.state.out == s.ctrl.STATE_MAX:
      state_str = "MAX "
    if s.ctrl.state.out == s.ctrl.STATE_DONE:
      state_str = "DONE"

    return "{} (count{} wr_data{} wr_addr{} wr_en{} rd_addr{} rd_dat{} qrdy{} qval{} prdy{} pval{} max{} idx{} {}) {}".format( s.req, 
            s.ctrl.init_count, s.dpath.knn_wr_data, s.ctrl.knn_wr_addr, s.dpath.knn_wr_en,
            s.dpath.knn_rd_addr, s.dpath.knn_rd_data,
            s.dpath.FindMax_req_rdy, s.dpath.FindMax_req_val, s.dpath.FindMax_resp_rdy, s.dpath.FindMax_resp_val,
            s.dpath.FindMax_resp_data, s.dpath.FindMax_resp_idx,
            state_str, s.resp )
