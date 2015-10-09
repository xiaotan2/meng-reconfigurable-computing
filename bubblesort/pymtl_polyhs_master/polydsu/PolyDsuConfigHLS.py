#=========================================================================
# PolyDsuConfigHLS
#=========================================================================
# Wrapper model for the HLS generated hardware

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from polydsu.PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg
from xmem.MemMsgFuture  import MemMsg

#-------------------------------------------------------------------------
# PolyDsuConfigHLS
#-------------------------------------------------------------------------

class PolyDsuConfigHLS( VerilogModel ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq     = InValRdyBundle  ( PolyDsuReqMsg()       )
    s.xcelresp    = OutValRdyBundle ( PolyDsuRespMsg()      )

    s.dstype_ce   = OutPort( 1 )
    s.dstype_we   = OutPort( 1 )
    s.dstype_data = OutPort( 4 )
    s.dstype_addr = OutPort( 5 )

    s.set_ports({
      'ap_clk'                   : s.clk,
      'ap_rst'                   : s.reset,
      'xcelreq_V_bits_V'         : s.xcelreq.msg,
      'xcelreq_V_bits_V_ap_vld'  : s.xcelreq.val,
      'xcelreq_V_bits_V_ap_ack'  : s.xcelreq.rdy,
      'xcelresp_V_bits_V'        : s.xcelresp.msg,
      'xcelresp_V_bits_V_ap_vld' : s.xcelresp.val,
      'xcelresp_V_bits_V_ap_ack' : s.xcelresp.rdy,
      'dstype_V_address0'        : s.dstype_addr,
      'dstype_V_ce0'             : s.dstype_ce,
      'dstype_V_we0'             : s.dstype_we,
      'dstype_V_d0'              : s.dstype_data,
  })
