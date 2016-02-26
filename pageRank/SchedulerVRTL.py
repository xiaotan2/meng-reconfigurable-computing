#=========================================================================
# SchedulerVRTL
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.ifcs   import MemReqMsg, MemRespMsg

from pageRankMsg  import *

class SchedulerVRTL( VerilogModel ):

  # Constructor

  def __init__( s, nbits = 32, nports = 2 ):

    #---------------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------------

    s.direq     = InValRdyBundle  ( pageRankReqMsg()  )
    s.diresp    = OutValRdyBundle ( pageRankRespMsg() )

    s.memreq    = [ OutValRdyBundle  ( MemReqMsg(8,32,32) ) for _ in range ( nports ) ]
    s.memresp   = [ InValRdyBundle   ( MemRespMsg(8,32)   ) for _ in range ( nports ) ]

    #---------------------------------------------------------------------------
    # Verilog import setup
    #---------------------------------------------------------------------------

    # verilog parameters
 
    s.set_params({
      'nbits'  : nbits,
      'nports' : nports
    })

    # verilog ports

    s.set_ports({
      'clk'             : s.clk,
      'reset'           : s.reset,

 #     'in_req_val'      : s.direq.val,
 #     'out_req_rdy'     : s.direq.rdy,
 #     'in_type'         : s.direq.msg.type_,
 #     'in_addr'         : s.direq.msg.addr,
 #     'in_data'         : s.direq.msg.data,

 #     'out_resp_val'    : s.diresp.val,
 #     'in_resp_rdy'     : s.diresp.rdy,
 #     'out_type'        : s.diresp.msg.type_,
 #     'out_data'        : s.diresp.msg.data,


      'mem_req0_msg'    : s.memreq[0].msg,
      'mem_req0_val'    : s.memreq[0].val,
      'mem_req0_rdy'    : s.memreq[0].rdy,

      'mem_resp0_msg'   : s.memresp[0].msg,
      'mem_resp0_val'   : s.memresp[0].val,
      'mem_resp0_rdy'   : s.memresp[0].rdy,

      'mem_req1_msg'    : s.memreq[1].msg,
      'mem_req1_val'    : s.memreq[1].val,
      'mem_req1_rdy'    : s.memreq[1].rdy,

      'mem_resp1_msg'   : s.memresp[1].msg,
      'mem_resp1_val'   : s.memresp[1].val,
      'mem_resp1_rdy'   : s.memresp[1].rdy,
    })


  def line_trace( s ):
    return "{}".format( s.memreq[0].msg )

