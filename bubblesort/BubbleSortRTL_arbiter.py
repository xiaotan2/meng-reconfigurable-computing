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
    s.reg_req_msg = Wire( Bits(32) )
    s.reg_req_val = Wire( Bits(1)  )
   
    # Response Register
    s.reg_resp_msg = Wire( Bits(32) )
    s.reg_resp_val = Wire( Bits(1)  )
    s.reg_resp_rdy = Wire( Bits(1)  )
   
    # Request Select
    s.req_sel     = Wire( Bits(1) )
    
    # Request Mux Output Wires
    s.req_msg_mux_out = Wire( Bits(32) )
    s.req_val_mux_out = Wire( Bits(1)  )
    
    s.req_rdy = Wire( Bits(1)  )

    # States
    s.STATE_FirReq = 0
    s.STATE_SecReq = 1

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
        s.memreq.msg.value = s.req_msg_mux_out
        s.memreq.val.value = s.req_val_mux_out
        s.memresp.rdy.value = s.reg_resp_rdy
      else:
        s.memreq.msg.value = s.duaxcelreq.msg
        s.memreq.val.value = s.duaxcelreq.val
        s.memresp.rdy.value = s.duaxcelresp.rdy
      
      s.xcelreq.rdy.value    = s.memreq.rdy
      s.duaxcelreq.rdy.value = s.memreq.rdy

      # dua xcel response
      s.duaxcelresp.msg.value = s.memresp.msg
      s.duaxcelresp.val.value = s.memresp.val

    #--------------------------------------------------------------
    # Ticking Concurrent Blocks
    #--------------------------------------------------------------

    @s.tick_rtl
    def updatRegister():
      if s.reset:
        # Request reg
        s.reg_req_msg.next = 0
        s.reg_req_val.next = 0
  
        # Response reg
        s.reg_resp_msg.next = 0
        s.reg_resp_val.next = 0
        s.reg_resp_rdy.next = 0
      else:
        # Request reg
        s.reg_req_msg.next = s.xcelreq.msg
        s.reg_req_val.next = s.xcelreq.val
        
        # Response reg
        s.reg_resp_msg.next = s.memresp.msg
        s.reg_resp_val.next = s.memresp.val
        s.reg_resp_rdy.next = s.xcelresp.rdy

    #--------------------------------------------------------------
    # Control Unit
    #--------------------------------------------------------------
    # reset states
    s.state = RegRst( 4, reset_value = s.STATE_FirReq )
 
    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():
      curr_state = s.state.out
      next_state = s.state.out

      if ( curr_state == s.STATE_FirReq ):
        if ( s.memreq.rdy and s.memresp.rdy ):
          next_state = s.STATE_SecReq
      
      if ( curr_state == s.STATE_SecReq ):
        if ( s.reg_req_rdy and s.memresp.rdy ):
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
      
      if ( current_state == s.STATE_SecReq ):
        s.req_sel.value = 1

    
