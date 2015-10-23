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
    
    s.req_rdy = Wire( Bits(2)  )

    # States
    s.STATE_FirReq = 0
    s.STATE_SecReq = 1
    s.STATE_Resp   = 2

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
        if ( s.xcelreq.val and s.duaxcelreq.val and
             s.memreq.rdy):
          next_state = s.STATE_SecReq

      if ( curr_state == s.STATE_SecReq ):
        if ( s.memreq.rdy and s.memresp.rdy ):
          next_state = s.STATE_Resp

      if ( curr_state == s.STATE_Resp ):
        if ( s.memresp.rdy):
          if ( s.xcelreq.val and s.duaxcelreq.val and
               s.memreq.rdy):
            next_state = s.STATE_SecReq
          else:
            next_state = s.STATE_FirReq

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------
    
    @s.combinational
    def state_outputs():
      current_state = s.state.out
      s.memresp.rdy.value = 0
      s.memreq.val.value  = 0
      s.xcelreq.rdy.value = 0
      s.duaxcelreq.rdy.value = 0
      s.xcelresp.val.value = 0
      s.duaxcelresp.val.value = 0

      s.req_sel.value = 0

      if ( current_state == s.STATE_FirReq ):
        if ( s.xcelreq.val and s.duaxcelreq.val and
             s.memreq.rdy):
          s.memreq.val.value = 1
          s.memreq.msg.value = s.duaxcelreq.msg
          s.xcelresp.val.value = 0
          s.duaxcelresp.val.value = 0
          s.xcelreq.rdy.value  = 0
          s.duaxcelreq.rdy.value = 0
        else:
          s.xcelresp.val.value = 0
          s.duaxcelresp.val.value = 0
          s.xcelreq.rdy.value  = 0
          s.duaxcelreq.rdy.value = 0
      
      if ( current_state == s.STATE_SecReq ):
        if (s.memreq.rdy and s.memresp.val):
          s.memreq.val.value = 1
          s.memreq.msg.value = s.xcelreq.msg
          s.memresp.rdy.value = 1
          s.duaxcelresp.msg.value = s.memresp.msg
          s.xcelreq.rdy.value  = 1
          s.duaxcelreq.rdy.value = 1
        else:
          s.xcelresp.val.value = 0
          s.duaxcelresp.val.value = 0
          s.xcelreq.rdy.value  = 0
          s.duaxcelreq.rdy.value = 0

      if ( current_state == s.STATE_Resp ):
        if (s.memresp.val):
          s.xcelresp.msg.value  = s.memresp.msg
          s.xcelresp.val.value  = 1
          s.duaxcelresp.val.value = 1
          s.memresp.rdy.value = 1
          if (s.memreq.rdy and 
              s.xcelreq.val and s.duaxcelreq.val):
            s.memreq.val.value = 1
            s.memreq.msg.value = s.duaxcelreq.msg
            s.xcelreq.rdy.value  = 0
            s.duaxcelreq.rdy.value = 0
          else:
            s.xcelreq.rdy.value  = 0
            s.duaxcelreq.rdy.value = 0
        else:
          s.xcelresp.val.value = 0
          s.duaxcelresp.val.value = 0

  def line_trace( s ):

    debug_str = "state:{}".format(s.state.out)
    xcel1 = "xcel1: req:v{}|r{}|a{} resp:v{}|r{}|d{}".format(
             s.xcelreq.val, s.xcelreq.rdy, s.xcelreq.msg.addr,
             s.xcelresp.val, s.xcelresp.rdy, s.xcelresp.msg.data)
    xcel2 = "xcel2: req:v{}|r{}|d{} resp:v{}|r{}".format(
             s.duaxcelreq.val, s.duaxcelreq.rdy, s.duaxcelreq.msg.data,
             s.duaxcelresp.val, s.duaxcelresp.rdy)
    read_req_str  = " r_req:v{}|r{}|a{}|t{}".format(
                            s.memreq.val, 
                            s.memreq.rdy, 
                            s.memreq.msg.addr, 
                            s.memreq.msg.type_)

    read_resp_str = " r_resp:v{}|r{}|d{}".format(
                            s.memresp.val, s.memresp.rdy, 
                            s.memresp.msg.data)

    write_req_str = " w_req:a{}|d{}".format(
                            s.memreq.msg.addr, 
                            s.memreq.msg.data)

    return debug_str + read_req_str + read_resp_str
