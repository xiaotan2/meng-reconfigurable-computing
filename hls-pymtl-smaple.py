#=========================================================================
# SortXcelHLS
#=========================================================================
# Wrapper module for HLS generated hardware

import os

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.ifcs   import valrdy_to_str
from pclib.rtl    import SingleElementBypassQueue
from pclib.rtl    import SingleElementPipelinedQueue
from dstu.XcelMsg import *
from dstu.MemMsgFuture import *
from hls_misc     import *

#-------------------------------------------------------------------------
# SortXcelHLS
#-------------------------------------------------------------------------

class SortXcelHLS( VerilogModel ):

  def __init__( s ):

    s.xcelreq  = InValRdyBundle ( XcelReqMsg()  )
    s.xcelresp = OutValRdyBundle( XcelRespMsg() )

    s.memreq   = OutValRdyBundle( MemReqMsg (18,32,32) )
    s.memresp  = InValRdyBundle ( MemRespMsg(8,32)    )

    s.set_ports({
      'ap_clk'            : s.clk,
      'ap_rst'            : s.reset,
      'xcelreq_V'         : s.xcelreq.msg,
      'xcelreq_V_ap_vld'  : s.xcelreq.val,
      'xcelreq_V_ap_ack'  : s.xcelreq.rdy,
      'xcelresp_V'        : s.xcelresp.msg,
      'xcelresp_V_ap_vld' : s.xcelresp.val,
      'xcelresp_V_ap_ack' : s.xcelresp.rdy,
      'memreq_V_bits_V'          : s.memreq.msg,
      'memreq_V_bits_V_ap_vld'   : s.memreq.val,
      'memreq_V_bits_V_ap_ack'   : s.memreq.rdy,
      'memresp_V_bits_V'         : s.memresp.msg,
      'memresp_V_bits_V_ap_vld'  : s.memresp.val,
      'memresp_V_bits_V_ap_ack'  : s.memresp.rdy
    })


class SortXcelHLS_Wrapper( Model ):

  def __init__( s ):

    s.xcelreq  = InValRdyBundle ( XcelReqMsg()  )
    s.xcelresp = OutValRdyBundle( XcelRespMsg() )

    s.memreq   = OutValRdyBundle( MemReqMsg (8,32,32) )
    s.memresp  = InValRdyBundle ( MemRespMsg(8,32)    )
    s.reqcon   = MemReqConnector( 18, 8 )

    s.xcel = SortXcelHLS()

    s.connect( s.xcelreq,   s.xcel.xcelreq )
    s.connect( s.xcelresp,  s.xcel.xcelresp )

    s.pq = SingleElementPipelinedQueue( MemRespMsg(8,32) )

    s.connect( s.memresp, s.pq.enq )
    s.connect( s.pq.deq, s.xcel.memresp )

    s.bq = SingleElementBypassQueue( MemReqMsg(8,32,32) )

    s.connect( s.bq.deq, s.memreq )
    s.connect( s.xcel.memreq.val, s.bq.enq.val )
    s.connect( s.xcel.memreq.rdy, s.bq.enq.rdy )

    s.connect( s.reqcon.in_, s.xcel.memreq )
    s.connect( s.reqcon.out, s.bq.enq )

  def line_trace(s):
    return "{}|{}".format(
      valrdy_to_str( s.xcel.memreq.msg, s.xcel.memreq.val, s.xcel.memreq.rdy ),
      valrdy_to_str( s.xcel.memresp.msg, s.xcel.memresp.val, s.xcel.memresp.rdy )
    )