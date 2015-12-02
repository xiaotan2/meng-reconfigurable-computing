#=========================================================================
# Reducer
#=========================================================================

import math

from pymtl         import *
from pclib.ifcs    import InValRdyBundle, OutValRdyBundle
from pclib.rtl     import RegEnRst, Mux, Adder, Subtractor, LtComparator, RegRst, RegisterFile, ZeroExtender

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

    SUM_DATA_SIZE         = int( math.ceil( math.log( 50*k, 2 ) ) ) 
  
    s.req_msg_data        = InPort (RE_DATA_SIZE) 
    s.resp_msg_digit      = OutPort(4)
  
    # ctrl->dpath
    s.knn_wr_data_mux_sel = InPort (1)
    s.knn_wr_addr         = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr         = InPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_wr_en           = InPort (1)
    
    s.vote_wr_data_mux_sel= InPort (1)
    s.vote_wr_addr        = InPort ( int( math.ceil( math.log( DIGIT, 2) ) ) ) # max 10
    s.vote_rd_addr        = InPort ( int( math.ceil( math.log( DIGIT, 2) ) ) ) # max 10
    s.vote_wr_en          = InPort (1)

    s.FindMax_req_val     = InPort (1) 
    s.FindMax_resp_rdy    = InPort (1)
    s.FindMin_req_val     = InPort (1) 
    s.FindMin_resp_rdy    = InPort (1)
  
    s.msg_data_reg_en     = InPort (1)
    s.msg_idx_reg_en      = InPort (1)

    # dpath->ctrl
    s.FindMax_req_rdy     = OutPort(1)
    s.FindMax_resp_val    = OutPort(1)
    s.FindMax_resp_idx    = OutPort( int( math.ceil( math.log( k, 2) ) ) ) # max 3
    s.FindMin_req_rdy     = OutPort(1)
    s.FindMin_resp_val    = OutPort(1)
    s.isSmaller           = OutPort(1)

    # internal wires     
    s.knn_rd_data         = Wire( Bits( RE_DATA_SIZE  ) )
    s.knn_wr_data         = Wire( Bits( RE_DATA_SIZE  ) )

    s.subtractor_out      = Wire( Bits( SUM_DATA_SIZE ) )
    s.adder_out           = Wire( Bits( SUM_DATA_SIZE ) )

    s.vote_rd_data        = Wire( Bits( SUM_DATA_SIZE ) )
    s.vote_wr_data        = Wire( Bits( SUM_DATA_SIZE ) )

    s.FindMax_req_data    = Wire( Bits( RE_DATA_SIZE  ) )
    s.FindMax_resp_data   = Wire( Bits( RE_DATA_SIZE  ) )
    s.FindMin_req_data    = Wire( Bits( SUM_DATA_SIZE ) )
    s.FindMin_resp_data   = Wire( Bits( SUM_DATA_SIZE ) )
    s.FindMin_resp_idx    = Wire( Bits( int( math.ceil( math.log( DIGIT, 2 ) ) ) ) ) # max 10

    # Req msg data Register
    s.req_msg_data_q = Wire( Bits( RE_DATA_SIZE ) )    

    s.req_msg_data_reg = m = RegEnRst( RE_DATA_SIZE )
    s.connect_dict({
      m.en      : s.msg_data_reg_en,
      m.in_     : s.req_msg_data,
      m.out     : s.req_msg_data_q
    })

    # knn_wr_data Mux
    s.knn_wr_data_mux = m = Mux( RE_DATA_SIZE, 2 )
    s.connect_dict({
      m.sel     : s.knn_wr_data_mux_sel,
      m.in_[0]  : 50,
      m.in_[1]  : s.req_msg_data_q,
      m.out     : s.knn_wr_data
    })

    
    # register file knn_table
    s.knn_table = m = RegisterFile( dtype=Bits(RE_DATA_SIZE), 
                      nregs=k*DIGIT, rd_ports=1, wr_ports=1, const_zero=False ) 
    s.connect_dict({
      m.rd_addr[0] : s.knn_rd_addr,
      m.rd_data[0] : s.knn_rd_data,
      m.wr_addr    : s.knn_wr_addr,
      m.wr_data    : s.knn_wr_data,
      m.wr_en      : s.knn_wr_en
    })



    # vote_wr_data Mux
    s.vote_wr_data_mux = m = Mux( SUM_DATA_SIZE, 2 )
    s.connect_dict({
      m.sel     : s.vote_wr_data_mux_sel,
      m.in_[0]  : 50*k,
      m.in_[1]  : s.adder_out,
      m.out     : s.vote_wr_data
    })


    # register file knn_vote
    s.knn_vote = m = RegisterFile( dtype=Bits( SUM_DATA_SIZE ),
                      nregs=DIGIT, rd_ports=1, wr_ports=1, const_zero=False )
    s.connect_dict({
      m.rd_addr[0] : s.vote_rd_addr,
      m.rd_data[0] : s.vote_rd_data,
      m.wr_addr    : s.vote_wr_addr,
      m.wr_data    : s.vote_wr_data,
      m.wr_en      : s.vote_wr_en
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


    # Less than comparator
    s.knn_LtComparator = m = LtComparator( RE_DATA_SIZE )
    s.connect_dict({
      m.in0 : s.req_msg_data_q,
      m.in1 : s.FindMax_resp_data,
      m.out : s.isSmaller
    })

    # Zero extender
    s.FindMax_resp_data_zext = Wire( Bits( SUM_DATA_SIZE ) )
    s.FindMax_resp_data_zexter = m = ZeroExtender( RE_DATA_SIZE, SUM_DATA_SIZE )
    s.connect_dict({
      m.in_     : s.FindMax_resp_data,
      m.out     : s.FindMax_resp_data_zext,
    })

    # Subtractor
    s.subtractor = m = Subtractor( SUM_DATA_SIZE )
    s.connect_dict({
      m.in0     : s.vote_rd_data,
      m.in1     : s.FindMax_resp_data_zext,
      m.out     : s.subtractor_out
    })

    # Zero extender
    s.req_msg_data_zext = Wire( Bits( SUM_DATA_SIZE ) )
    s.req_msg_data_zexter = m = ZeroExtender( RE_DATA_SIZE, SUM_DATA_SIZE )
    s.connect_dict({
      m.in_     : s.req_msg_data_q,
      m.out     : s.req_msg_data_zext,
    })

    # Adder    
    s.adder = m = Adder( SUM_DATA_SIZE )
    s.connect_dict({
      m.in0     : s.subtractor_out,
      m.in1     : s.req_msg_data_zext,
      m.cin     : 0,
      m.out     : s.adder_out
    })


    # Find min value of knn_vote, return digit
    s.connect_wire( s.vote_rd_data, s.FindMin_req_data )
    
    s.findmin   = m = FindMinPRTL( SUM_DATA_SIZE, DIGIT )
    s.connect_dict({
      m.req.val       : s.FindMin_req_val,
      m.req.rdy       : s.FindMin_req_rdy,
      m.req.msg.data  : s.FindMin_req_data,
      m.resp.val      : s.FindMin_resp_val,
      m.resp.rdy      : s.FindMin_resp_rdy,
      m.resp.msg.data : s.FindMin_resp_data,
      m.resp.msg.digit: s.FindMin_resp_idx
    })


    # Resp idx Register
    s.resp_msg_idx_q = Wire( Bits( int( math.ceil( math.log( DIGIT, 2 ) ) ) ) )

    s.req_msg_idx_reg = m = RegEnRst( int( math.ceil( math.log( DIGIT, 2 ) ) ) )
    s.connect_dict({
      m.en      : s.msg_idx_reg_en,
      m.in_     : s.FindMin_resp_idx,
      m.out     : s.resp_msg_idx_q
    })

    # connect output idx
    s.connect( s.resp_msg_idx_q, s.resp_msg_digit )


#=========================================================================
# Reducer Control
#=========================================================================

class ReducerCtrl (Model):

  def __init__( s, k = 3 ):
 
    # ctrl to toplevel
    s.req_val             = InPort  (1)
    s.req_rdy             = OutPort (1)

    s.resp_val            = OutPort (1)
    s.resp_rdy            = InPort  (1)

    s.req_msg_digit       = InPort  (4)

    s.req_msg_type        = InPort  (2)    
    s.resp_msg_type       = OutPort (2)    

    # ctrl->dpath
    s.knn_wr_data_mux_sel = OutPort (1)
    s.knn_wr_addr         = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_rd_addr         = OutPort ( int( math.ceil( math.log( k*DIGIT, 2) ) ) ) # max 30
    s.knn_wr_en           = OutPort (1)

    s.vote_wr_data_mux_sel= OutPort (1)
    s.vote_wr_addr        = OutPort ( int( math.ceil( math.log( DIGIT, 2) ) ) ) # max 10
    s.vote_rd_addr        = OutPort ( int( math.ceil( math.log( DIGIT, 2) ) ) ) # max 10
    s.vote_wr_en          = OutPort (1)

    s.FindMax_req_val     = OutPort (1) 
    s.FindMax_resp_rdy    = OutPort (1)
    s.FindMin_req_val     = OutPort (1) 
    s.FindMin_resp_rdy    = OutPort (1)

    s.msg_data_reg_en     = OutPort (1)
    s.msg_idx_reg_en      = OutPort (1)

    # dpath->ctrl
    s.FindMax_req_rdy     = InPort  (1)
    s.FindMax_resp_val    = InPort  (1)
    s.FindMax_resp_idx    = InPort  ( int( math.ceil( math.log( k, 2) ) ) ) # max 10
    s.FindMin_req_rdy     = InPort  (1)
    s.FindMin_resp_val    = InPort  (1)
    s.isSmaller           = InPort  (1)

    s.msg_type_reg_en     = Wire ( Bits(1) )
    s.msg_digit_reg_en    = Wire ( Bits(1) )
    s.req_msg_digit_q     = Wire ( Bits(4) )
    s.init_go             = Wire ( Bits(1) )
    s.max_go              = Wire ( Bits(1) )
    s.min_go              = Wire ( Bits(1) )

    # State element
    s.STATE_IDLE = 0
    s.STATE_INIT = 1
    s.STATE_MAX  = 2
    s.STATE_MIN  = 3
    s.STATE_DONE = 4

    s.state = RegRst( 3, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count  = Wire ( int( math.ceil( math.log( k*DIGIT, 2 ) ) ) ) # max 30
    s.knn_count   = Wire ( int( math.ceil( math.log( k*DIGIT, 2 ) ) ) ) # max 30
    s.vote_count  = Wire ( int( math.ceil( math.log( DIGIT,   2 ) ) ) ) # max 10

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

      if ( s.min_go == 1 ):
        s.vote_count.next  = s.vote_count  + 1
      else:
        s.vote_count.next  = 0

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
        elif ( (s.req_val and s.req_rdy) and (s.req_msg_type == 2)
                  and (s.FindMin_req_val and s.FindMin_req_rdy) ):
           next_state = s.STATE_MIN

      # Transition out of INIT state
      if ( curr_state == s.STATE_INIT ):
        if ( s.init_count == k*DIGIT - 1 ):
           next_state = s.STATE_DONE 

      # Transition out of MAX  state
      if ( curr_state == s.STATE_MAX  ):
        if ( s.FindMax_resp_val and s.FindMax_resp_rdy ):
           next_state = s.STATE_DONE 
      
      # Transition out of MIN  state
      if ( curr_state == s.STATE_MIN  ):
        if ( s.FindMin_resp_val and s.FindMin_resp_rdy ):
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
      
        s.msg_data_reg_en.value  = 1 
        s.msg_digit_reg_en.value = 1
        s.msg_type_reg_en.value  = 1
       
        s.init_go.value          = 0

        s.knn_wr_data_mux_sel.value = 0
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
         
        s.vote_wr_data_mux_sel.value   = 1
        s.vote_wr_en.value             = 0
        s.vote_wr_addr.value           = s.req_msg_digit_q
        s.vote_rd_addr.value           = s.req_msg_digit_q

      # INI state
      elif current_state == s.STATE_INIT:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
       
        s.msg_data_reg_en.value  = 0 
        s.msg_digit_reg_en.value = 0
        s.msg_type_reg_en.value  = 0
       
        s.init_go.value          = 1
        s.max_go.value           = 0
      
        s.knn_wr_data_mux_sel.value = 0
        s.knn_wr_en.value        = 1
        s.knn_wr_addr.value      = s.init_count
        s.FindMax_req_val.value  = 0 
        s.FindMax_resp_rdy.value = 0
        # knn_rd for debugging 
        if s.init_count == 0:
          s.knn_rd_addr.value    = 0
        else:
          s.knn_rd_addr.value    = s.init_count - 1

        if ( s.init_count < DIGIT ):
          s.vote_wr_data_mux_sel.value   = 0
          s.vote_wr_en.value             = 1
          s.vote_wr_addr.value           = s.init_count
          # vote_rd for debugging
          if s.init_count == 0:
            s.vote_rd_addr.value         = 0
          else:
            s.vote_rd_addr.value         = s.init_count - 1
        else:
          s.vote_wr_data_mux_sel.value   = 1
          s.vote_wr_en.value             = 0
          s.vote_wr_addr.value           = 0
          s.vote_rd_addr.value           = 0

      # MAX state
      elif current_state == s.STATE_MAX:
        s.req_rdy.value          = 0
        s.resp_val.value         = 0
       
        s.msg_data_reg_en.value  = 0 
        s.msg_digit_reg_en.value = 0
        s.msg_type_reg_en.value  = 0
       
        s.init_go.value          = 0
        s.max_go.value           = 1
      
        s.FindMax_req_val.value  = 1 
        s.FindMax_resp_rdy.value = 1
        if ( s.knn_count > s.req_msg_digit_q*k+2 ):
          s.knn_rd_addr.value    = 0
          s.knn_wr_addr.value    = s.req_msg_digit_q*k + s.FindMax_resp_idx
          if ( s.isSmaller == 1 ):
            s.knn_wr_data_mux_sel.value = 1
            s.knn_wr_en.value    = 1
            s.vote_wr_en.value   = 1
          else:
            s.knn_wr_data_mux_sel.value = 0
            s.knn_wr_en.value    = 0
        else:
          s.knn_wr_data_mux_sel.value = 0
          s.knn_rd_addr.value    = s.knn_count
          s.knn_wr_en.value      = 0
          s.knn_wr_addr.value    = 0
          s.vote_wr_en.value     = 0

        s.vote_wr_data_mux_sel.value   = 1
        s.vote_wr_addr.value           = s.req_msg_digit_q
        s.vote_rd_addr.value           = s.req_msg_digit_q

      # DONE state
      elif current_state == s.STATE_DONE:
        s.req_rdy.value          = 0
        s.resp_val.value         = 1
      
        s.msg_data_reg_en.value  = 0 
        s.msg_digit_reg_en.value = 0
        s.msg_type_reg_en.value  = 0
      
        s.init_go.value          = 0
        s.max_go.value           = 0
    
        s.knn_wr_data_mux_sel.value = 0
        s.knn_wr_en.value        = 0
        s.knn_wr_addr.value      = 0
        s.FindMax_req_val.value  = 0 
        s.FindMax_resp_rdy.value = 0
        s.knn_rd_addr.value      = 0x1b

        s.vote_wr_data_mux_sel.value   = 1
        s.vote_wr_en.value             = 0
        s.vote_wr_addr.value           = s.req_msg_digit_q
        s.vote_rd_addr.value           = s.req_msg_digit_q

    # Register for resp msg type     
    s.Reg_msg_type = m = RegEnRst( 2 )
    s.connect_dict({
      m.en  : s.msg_type_reg_en,
      m.in_ : s.req_msg_type,
      m.out : s.resp_msg_type,
    })
 

    # Register for req msg digit
    s.Reg_msg_digit = m = RegEnRst( 4 )
    s.connect_dict({
      m.en  : s.msg_digit_reg_en,
      m.in_ : s.req_msg_digit,
      m.out : s.req_msg_digit_q,
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

    return "{} (ct{} | wr_data{} wr_addr{} wr_en{} rd_addr{} rd_dat{} | wr_data{} wr_addr{} wr_en{} rd_addr{} rd_dat{} | qrv{}{} prv{}{} | in{}<?max{} idx{} sma{} {}) {}".format( s.req, 
            s.ctrl.init_count,
            s.dpath.knn_wr_data, s.dpath.knn_wr_addr, s.dpath.knn_wr_en,
            s.dpath.knn_rd_addr, s.dpath.knn_rd_data,
            s.dpath.vote_wr_data, s.dpath.vote_wr_addr, s.dpath.vote_wr_en,
            s.dpath.vote_rd_addr, s.dpath.vote_rd_data,
            s.dpath.FindMax_req_rdy, s.dpath.FindMax_req_val, s.dpath.FindMax_resp_rdy, s.dpath.FindMax_resp_val,
            s.dpath.req_msg_data_q, s.dpath.FindMax_resp_data, s.dpath.FindMax_resp_idx, s.ctrl.isSmaller,
            state_str, s.resp )
