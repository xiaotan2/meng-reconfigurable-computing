#=========================================================================
# PolyDsuBinTree
#=========================================================================
# Top-level model that composes a PolyDsuBinTreeHLS model and a PolyDsuConfig
# model that tests the bintree accelerator in isolation

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import valrdy_to_str

from pclib.rtl  import RegisterFile
from pclib.rtl  import SingleElementBypassQueue

from polydsu.PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg
from xmem.MemMsgFuture  import MemMsg

from PolyDsuBinTreeHLS  import PolyDsuBinTreeHLS

from polydsu.PolyDsuConfigHLS  import PolyDsuConfigHLS

from misc.FunnelRouter import FunnelRouter

#-------------------------------------------------------------------------
# PolyDsuBinTree
#-------------------------------------------------------------------------

class PolyDsuBinTree( Model ):

  def __init__( s ):

    s.DSTU_ID  = 3

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq  = InValRdyBundle  ( PolyDsuReqMsg()  )
    s.xcelresp = OutValRdyBundle ( PolyDsuRespMsg() )

    s.memreq   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    #---------------------------------------------------------------------
    # Model instantations
    #---------------------------------------------------------------------

    # config manager
    s.config_hls = PolyDsuConfigHLS()

    # bintree xcel
    s.bintree_hls = PolyDsuBinTreeHLS()

    # state
    s.dstype_rf  = RegisterFile( dtype=4  )

    # shreesha: required for gem5-pymtl integration
    # bypass queue xcelreq
    s.xcelreq_q = SingleElementBypassQueue( PolyDsuReqMsg() )
    s.connect( s.xcelreq, s.xcelreq_q.enq )

    # shreesha: required for gem5-pymtl integration
    # bypass queue for memresp
    s.memresp_q = SingleElementBypassQueue( MemMsg(8,32,32).resp )
    s.connect( s.memresp, s.memresp_q.enq )

    #---------------------------------------------------------------------
    # Connections
    #---------------------------------------------------------------------

    s.ds_id = Wire ( 5 )

    @s.combinational
    def comb():
      s.ds_id.value = s.xcelreq.msg.id & 0x1f

    # config_hls <-> dstype_rf connections
    s.connect( s.dstype_rf.wr_en,      s.config_hls.dstype_we   )
    s.connect( s.dstype_rf.wr_addr,    s.config_hls.dstype_addr )
    s.connect( s.dstype_rf.wr_data,    s.config_hls.dstype_data )
    s.connect( s.dstype_rf.rd_addr[0], s.ds_id                  )

    # no need of lookup for a single xcel
    #s.connect( s.dstype_rf.rd_data[0], s.dsu_router.id          )

    #---------------------------------------------------------------------
    # Route the xcelreq and xcelresp msgs
    #---------------------------------------------------------------------

    @s.combinational
    def xcel_connections():

      # xcelreq msg
      s.xcelreq_q.deq.rdy.value      = 0
      s.config_hls.xcelreq.val.value = 0
      s.config_hls.xcelreq.msg.value = 0
      s.bintree_hls.xcelreq.val.value = 0
      s.bintree_hls.xcelreq.msg.value = 0

      if   s.xcelreq_q.deq.msg.id == s.DSTU_ID:
        s.config_hls.xcelreq.val.value = s.xcelreq_q.deq.val
        s.config_hls.xcelreq.msg.value = s.xcelreq_q.deq.msg
        s.xcelreq_q.deq.rdy.value      = s.config_hls.xcelreq.rdy

      elif ( s.xcelreq_q.deq.msg.id & 0x400 ):
        s.bintree_hls.xcelreq.val.value = s.xcelreq_q.deq.val
        s.bintree_hls.xcelreq.msg.value = s.xcelreq_q.deq.msg
        s.xcelreq_q.deq.rdy.value      = s.bintree_hls.xcelreq.rdy

      # xcelresp msg
      # NOTE: prioritize the cfg responses over the bintree responses
      s.xcelresp.val.value            = 0
      s.xcelresp.msg.value            = 0
      s.config_hls.xcelresp.rdy.value = 0
      s.bintree_hls.xcelresp.rdy.value = 0
      if   s.config_hls.xcelresp.val:
        s.xcelresp.val.value = s.config_hls.xcelresp.val
        s.xcelresp.msg.value = s.config_hls.xcelresp.msg
        s.config_hls.xcelresp.rdy.value = s.xcelresp.rdy
      elif s.bintree_hls.xcelresp.val:
        s.xcelresp.val.value = s.bintree_hls.xcelresp.val
        s.xcelresp.msg.value = s.bintree_hls.xcelresp.msg
        s.bintree_hls.xcelresp.rdy.value = s.xcelresp.rdy

    # mem connections
    s.connect( s.bintree_hls.memreq,  s.memreq        )
    s.connect( s.bintree_hls.memresp, s.memresp_q.deq )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {}|{} {}".format(
      s.xcelreq,
      s.xcelresp,
      s.memreq,
      s.memresp,
    )
