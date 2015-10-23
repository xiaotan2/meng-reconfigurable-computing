from pymtl        import *
from pclib.rtl    import Mux, RegRst
from pclib.ifcs import MemMsg, MemReqMsg4B, MemRespMsg4B
from pclib.rtl  import SingleElementBypassQueue, SingleElementPipelinedQueue, TwoElementBypassQueue

from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.fl   import InValRdyQueueAdapter, OutValRdyQueueAdapter
from pclib.fl   import ListMemPortAdapter
 
from xcel.XcelMsg      import XcelReqMsg, XcelRespMsg
from xmem.MemMsgFuture import MemMsg, MemReqMsg, MemRespMsg
 
 
class BSArbiter ( Model ) :
 
  # Constructor

  def __init__( s, mem_msg = MemMsg( 8, 32, 32 ) ):

    #--------------------------------------------------------------
    # Interface
    #--------------------------------------------------------------

    s.memreq          = OutValRdyBundle( mem_msg.req()  )
    s.memresp         = InValRdyBundle ( mem_msg.resp() )
    
    s.xcelreq         = InValRdyBundle ( mem_msg.req()   )
    s.xcelresp        = OutValRdyBundle( mem_msg.resp()  )

    s.duaxcelreq      = InValRdyBundle ( mem_msg.req()   )
    s.duaxcelresp     = OutValRdyBundle( mem_msg.resp()  )

    #--------------------------------------------------------------
    # Registers, Wires, Parameters
    #--------------------------------------------------------------

    # Request Register 
    s.reg1_req_msg = Wire( Bits(77) )
    s.reg1_req_val = Wire( Bits(1)  )
    # a wire
    s.arbitor_rdy = Wire( Bits(1)  )
   
    # Response Register
    s.reg1_resp_rdy = Wire( Bits(1)  )
   
    s.reg2_duaxcelresp_msg = Wire( Bits(77) )
    s.reg2_duaxcelresp_val = Wire( Bits(1)  )
    
    s.reg2_msg_wire = Wire( Bits(77) )
    s.reg2_val_wire = Wire( Bits(1)  ) 
    
    # Request Select
    s.req_sel     = Wire( Bits(1) )
    
    # States
    s.STATE_FirReq        = 0
    s.STATE_FirRespSecReq = 1
    s.STATE_SecRespFirReq = 2
    s.STATE_SecResp       = 3
    #--------------------------------------------------------------
    # Data path
    #--------------------------------------------------------------
    #--------------------------------------------------------------
    # Combinational Logic
    #--------------------------------------------------------------

    @s.combinational
    def comb_logic():
      # Request Mux
      if s.req_sel:
        s.memreq.msg.value = s.reg1_req_msg
        s.memreq.val.value = s.reg1_req_val
        s.memresp.rdy.value = s.reg1_resp_rdy

        s.xcelresp.msg.value = s.memresp.msg
        s.xcelresp.val.value = s.memresp.val
        s.reg2_msg_wire.value = s.reg2_duaxcelresp_msg
        s.reg2_val_wire.value = s.reg2_duaxcelresp_val
      else:
        s.memreq.msg.value = s.duaxcelreq.msg
        s.memreq.val.value = s.duaxcelreq.val
        s.memresp.rdy.value = s.duaxcelresp.rdy

      s.xcelreq.rdy.value    = s.memreq.rdy
      s.duaxcelreq.rdy.value = s.memreq.rdy

      # dua xcel response
      s.duaxcelresp.msg.value = s.memresp.msg
      s.duaxcelresp.val.value = s.memresp.val

      # s.reg2_duaxcelresp_msg.value = s.memresp.msg
      # s.reg2_duaxcelresp_val.value = s.memresp.val
      s.reg2_msg_wire.value = s.memresp.msg
      s.reg2_val_wire.value = s.memresp.val
      s.xcelresp.msg.value = 0
      s.xcelresp.val.value = 0
      
      s.xcelreq.rdy.value    = s.memreq.rdy and s.arbitor_rdy
      s.duaxcelreq.rdy.value = s.memreq.rdy and s.arbitor_rdy
    
      s.duaxcelresp.msg.value = s.reg2_duaxcelresp_msg
      s.duaxcelresp.val.value = s.reg2_duaxcelresp_val
    #--------------------------------------------------------------
    # Ticking Concurrent Blocks
    #--------------------------------------------------------------

    @s.tick_rtl
    def updatRegister():
      if s.reset:
        # Request reg
        s.reg1_req_msg.next = 0
        s.reg1_req_val.next = 0
  
        # Response reg
        s.reg1_resp_rdy.next = 0
        s.reg2_duaxcelresp_msg.next = 0
        s.reg2_duaxcelresp_val.next = 0
      else:
        # Request reg
        s.reg1_req_msg.next = s.xcelreq.msg
        s.reg1_req_val.next = s.xcelreq.val
        s.reg2_duaxcelresp_msg.next = s.reg2_msg_wire
        s.reg2_duaxcelresp_val.next = s.reg2_val_wire
        
        # Response reg
        s.reg1_resp_rdy.next = s.xcelresp.rdy

    #--------------------------------------------------------------
    # Control Unit
    #--------------------------------------------------------------
    # reset states

    s.state = RegRst( 2, reset_value = s.STATE_FirReq )
 
    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():
      curr_state = s.state.out
      next_state = s.state.out

      if ( curr_state == s.STATE_FirReq ):
        if ( s.duaxcelreq.val and s.memreq.rdy ):
          next_state = s.STATE_FirRespSecReq
      
      if ( curr_state == s.STATE_FirRespSecReq ):
        if ( s.memresp.val and s.duaxcelresp.rdy and s.memreq.rdy and s.reg1_req_val):
#        ( s.xcelreq.val and s.memreq.rdy and s.memresp.val and s.duaxcelresp.rdy ):
          next_state = s.STATE_SecResp

      if ( curr_state == s.STATE_SecRespFirReq ):
        if ( s.memresp.val and s.reg1_resp_rdy and s.memreq.rdy and s.duaxcelreq.val ):
          next_state = s.STATE_FirRespSecReq
        elif ( s.memresp.val and s.reg1_resp_rdy ):
          next_state = s.STATE_SecResp

      if ( curr_state == s.STATE_SecResp ):
        if ( s.memresp.val and s.reg1_resp_rdy):
#        ( s.memresp.val and s.xcelresp.rdy ):
          next_state = s.STATE_FirReq

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------
    
    @s.combinational
    def state_outputs():
      current_state = s.state.out

      s.req_sel.value = 0

      if ( current_state == s.STATE_FirReq ):
        s.req_sel.value = 0
        s.arbitor_rdy.value = 1
      
      if ( current_state == s.STATE_FirRespSecReq ):
        s.req_sel.value = 1
        s.arbitor_rdy.value = 0
      
      if ( current_state == s.STATE_SecRespFirReq ):
        s.req_sel.value = 0
        s.arbitor_rdy.value = 0
      
      if ( current_state == s.STATE_SecResp ):
        s.req_sel.value = 1
        s.arbitor_rdy.value = 0

  def line_trace( s ):
    
    xcel_req_str  = " x_req:v{}$r{}$a{}$d{}$t{}".format(
                            s.xcelreq.val, s.xcelreq.rdy,
                            s.xcelreq.msg.addr,
                            s.xcelreq.msg.data,
                            s.xcelreq.msg.type_)


    duaxcel_req_str  = " x_duareq:v{}$r{}$a{}$d{}$t{}$sel{}$state{}".format(
                            s.duaxcelreq.val, s.duaxcelreq.rdy,
                            s.duaxcelreq.msg.addr,
                            s.duaxcelreq.msg.data,
                            s.duaxcelreq.msg.type_, s.req_sel.value, s.state.out)

    state_trans_str  = " x_state:{}s0<{}|{}>s1<{}|{}|{}|{}>s2<{}|{}|{}|{}>s3<{}|{}>bubble_cond:<{}|{}>".format(
                            s.state.out,
                            s.duaxcelreq.val, s.memreq.rdy, 
                            s.duaxcelresp.rdy, s.memresp.val, s.reg1_req_val, s.memreq.rdy,
                            s.reg1_resp_rdy, s.memresp.val, s.duaxcelreq.val, s.memreq.rdy,
                            s.memresp.val, s.reg1_resp_rdy,
                            s.duaxcelreq.rdy, s.xcelreq.rdy)

    read_req_str  = " r_req:v{}|r{}|a{}|t{}".format(
                            s.memreq.val,
                            s.memreq.rdy,
                            s.memreq.msg.addr,
                            s.memreq.msg.type_)
    

    line_str = (read_req_str)
    line_str = (duaxcel_req_str)
    line_str = (state_trans_str)
    return line_str

 
