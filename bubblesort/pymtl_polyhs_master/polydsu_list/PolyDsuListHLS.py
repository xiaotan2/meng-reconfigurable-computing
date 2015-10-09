#=========================================================================
# PolyDsuListHLS
#=========================================================================
# Wrapper model for the HLS generated hardware

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import valrdy_to_str

from polydsu.PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg
from xmem.MemMsgFuture  import MemMsg

class PolyDsuListHLS( VerilogModel ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq  = InValRdyBundle  ( PolyDsuReqMsg()  )
    s.xcelresp = OutValRdyBundle ( PolyDsuRespMsg() )

    s.memreq   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    s.set_ports({
      'ap_clk'                   : s.clk,
      'ap_rst'                   : s.reset,
      'xcelreq_V_bits_V'         : s.xcelreq.msg,
      'xcelreq_V_bits_V_ap_vld'  : s.xcelreq.val,
      'xcelreq_V_bits_V_ap_ack'  : s.xcelreq.rdy,
      'xcelresp_V_bits_V'        : s.xcelresp.msg,
      'xcelresp_V_bits_V_ap_vld' : s.xcelresp.val,
      'xcelresp_V_bits_V_ap_ack' : s.xcelresp.rdy,
      'memreq_V_bits_V'          : s.memreq.msg,
      'memreq_V_bits_V_ap_vld'   : s.memreq.val,
      'memreq_V_bits_V_ap_ack'   : s.memreq.rdy,
      'memresp_V_bits_V'         : s.memresp.msg,
      'memresp_V_bits_V_ap_vld'  : s.memresp.val,
      'memresp_V_bits_V_ap_ack'  : s.memresp.rdy
  })

  def line_trace( s ):
    return "{} | {} {} | {}".format(
      valrdy_to_str( s.xcelreq.msg,
                     s.xcelreq.val,
                     s.xcelreq.rdy ),
      valrdy_to_str( s.memreq.msg,
                     s.memreq.val,
                     s.memreq.rdy ),
      valrdy_to_str( s.memresp.msg,
                     s.memresp.val,
                     s.memresp.rdy ),
      valrdy_to_str( s.xcelresp.msg,
                     s.xcelresp.val,
                     s.xcelresp.rdy )
    )

