#=========================================================================
# SchedulerVRTL
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.ifcs   import MemReqMsg, MemRespMsg

from pageRankMsg  import *

class SchedulerVRTL( VerilogModel ):

  vlinetrace = True

  # Constructor

  def __init__( s, nbits = 8, nports = 1, bw = 32, n = 8,  ):

    #---------------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------------

    s.direq     = InValRdyBundle  ( pageRankReqMsg()  )
    s.diresp    = OutValRdyBundle ( pageRankRespMsg() )

    s.memreq    = OutValRdyBundle  ( MemReqMsg(8,32,32) ) 
    s.memresp   = InValRdyBundle   ( MemRespMsg(8,32)   ) 

    #---------------------------------------------------------------------------
    # Verilog import setup
    #---------------------------------------------------------------------------

    # verilog parameters
 
    s.set_params({
      'nbits'  : nbits,
      'nports' : nports,
      'bw'     : bw,
      'n'      : n
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

      'pr_req_msg'     : s.direq.msg,
      'pr_req_val'     : s.direq.val,
      'pr_req_rdy'     : s.direq.rdy,

      'pr_resp_msg'    : s.diresp.msg,
      'pr_resp_val'    : s.diresp.val,
      'pr_resp_rdy'    : s.diresp.rdy,

      'mem_req_msg'    : s.memreq.msg,
      'mem_req_val'    : s.memreq.val,
      'mem_req_rdy'    : s.memreq.rdy,

      'mem_resp_msg'   : s.memresp.msg,
      'mem_resp_val'   : s.memresp.val,
      'mem_resp_rdy'   : s.memresp.rdy,

    })


#  def line_trace( s ):
#    return "q({}):v({}):r({}) p({}):v({}):r({}) | req {} resp {} req{} resp {}".format(
#            s.direq.msg, s.direq.val, s.direq.rdy, 
#            s.diresp.msg, s.diresp.val, s.diresp.rdy,
#            s.memreq[0].msg, s.memresp[0].msg, s.memreq[1].msg, s.memresp[1].msg )
#
