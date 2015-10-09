#=========================================================================
# PolyDsuBinTreeO3
#=========================================================================
# Top-level model that composes a PolyDsuBinTreeHLS model and a PolyDsuConfig
# model that tests the bintree accelerator in isolation with the gem5 O3 model

from pymtl      import *

from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import valrdy_to_str

from pclib.rtl  import RegisterFile
from pclib.rtl  import SingleElementNormalQueue
from pclib.rtl  import SingleElementBypassQueue

from polydsu.PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg
from xmem.MemMsgFuture  import MemMsg

from PolyDsuBinTreeHLS  import PolyDsuBinTreeHLS

from polydsu.PolyDsuConfigHLS  import PolyDsuConfigHLS

from misc.FunnelRouter import FunnelRouter

from polydsu_lsq.PolyDsuLSQ import PolyDsuLSQ
from polydsu_lsq.CommitMsg  import CommitReqMsg, CommitRespMsg

#-------------------------------------------------------------------------
# PolyDsuBinTreeO3
#-------------------------------------------------------------------------

class PolyDsuBinTreeO3( Model ):

  def __init__( s ):

    s.DSTU_ID  = 3

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq    = InValRdyBundle  ( PolyDsuReqMsg()  )
    s.xcelresp   = OutValRdyBundle ( PolyDsuRespMsg() )

    s.memreq     = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp    = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    s.commitreq  = InValRdyBundle   ( CommitReqMsg()  )
    s.commitresp = OutValRdyBundle  ( CommitRespMsg() )

    #---------------------------------------------------------------------
    # Model instantations
    #---------------------------------------------------------------------

    # config manager
    s.config_hls = PolyDsuConfigHLS()

    # bintree xcel
    s.bintree_hls   = PolyDsuBinTreeHLS()

    # bintree lsq
    # NOTE: CURRENTLY SETTING THE LSQ TO HAVE A LARGE NUMBER OF ENTRIES AS
    # THE NUMBER OF ENTRIES FOR THE RBTREE LSQ IS DATA-DEPENDENT AND NEEDS
    # TO BE SIZED CORRECTLY ELSE THE UBMARK-INSERT STALLS.
    s.bintree_lsq   = PolyDsuLSQ( 1024 )

    # state
    s.dstype_rf  = RegisterFile( dtype=4  )

    # shreesha:
    # NEED A BYPASS QUEUE HERE BECAUSE OF A GEM5 INTEGRATION ISSUE.
    # When the xcel wrapper was integrated to the gem5 o3 model I ran into
    # a scenario where gem5 assumed that an xcel transaction would succeed
    # (by calling eval combinational) and advanced its pipeline stages. In
    # reality the xcel never really accepts the transaction when the tick
    # is called (which I caught by using the linetraces). Further I could
    # not reproduce this corner case using assembly tests and ran into it
    # only when writing a test C++ program. I am not sure what is going on.
    # However, the workaround is to have a single-element bypass queue, as
    # the gem5 o3 model can only send a single xcel request currently,
    # which provides a spot for the incoming transaction even when the xcel
    # is busy. And the queue handles the transaction fine.
    #
    # I think the reason why we can't catch these bugs in isolation is
    # because gem5 updates the input signals to the accelerator based on a
    # certain order and it checks the success of a val-rdy protocol
    # handshake based on that order alone. In reality if all the inputs
    # were concurrently applied the xcel may or may not service all the
    # val-rdy ports but there is no way to reproduce that purely in RTL! In
    # general it maybe okay to add these bypass queues for gem5
    # integration.
    s.xcelreq_q = SingleElementBypassQueue( PolyDsuReqMsg() )
    s.connect( s.xcelreq, s.xcelreq_q.enq )

    # shreesha: required for gem5-pymtl integration
    # bypass queue for memresp
    s.memresp_q = SingleElementBypassQueue( MemMsg(8,32,32).resp )
    s.connect( s.memresp, s.memresp_q.enq )

    # shreesha: required for gem5-pymtl integration
    # bypass queue for memresp
    s.commitreq_q = SingleElementBypassQueue( CommitReqMsg() )
    s.connect( s.commitreq, s.commitreq_q.enq )

    #---------------------------------------------------------------------
    # Connections
    #---------------------------------------------------------------------

    s.ds_id = Wire ( 5 )

    @s.combinational
    def comb():
      s.ds_id.value = s.xcelreq_q.deq.msg.id & 0x1f

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
      s.bintree_hls.xcelreq.val.value   = 0
      s.bintree_hls.xcelreq.msg.value   = 0

      if   s.xcelreq_q.deq.msg.id == s.DSTU_ID:
        s.config_hls.xcelreq.val.value = s.xcelreq_q.deq.val
        s.config_hls.xcelreq.msg.value = s.xcelreq_q.deq.msg
        s.xcelreq_q.deq.rdy.value      = s.config_hls.xcelreq.rdy

      elif ( s.xcelreq_q.deq.msg.id & 0x400 ):
        s.bintree_hls.xcelreq.val.value = s.xcelreq_q.deq.val
        s.bintree_hls.xcelreq.msg.value = s.xcelreq_q.deq.msg
        s.xcelreq_q.deq.rdy.value    = s.bintree_hls.xcelreq.rdy

      # xcelresp msg
      # NOTE: prioritize the cfg responses over the bintree responses
      s.xcelresp.val.value            = 0
      s.xcelresp.msg.value            = 0
      s.config_hls.xcelresp.rdy.value = 0
      s.bintree_hls.xcelresp.rdy.value   = 0
      if   s.config_hls.xcelresp.val:
        s.xcelresp.val.value            = s.config_hls.xcelresp.val
        s.xcelresp.msg.value            = s.config_hls.xcelresp.msg
        s.config_hls.xcelresp.rdy.value = s.xcelresp.rdy
      elif s.bintree_hls.xcelresp.val:
        s.xcelresp.val.value            = s.bintree_hls.xcelresp.val
        s.xcelresp.msg.value            = s.bintree_hls.xcelresp.msg
        s.bintree_hls.xcelresp.rdy.value = s.xcelresp.rdy

    # mem connections
    s.connect( s.bintree_hls.memreq,  s.bintree_lsq.memreq_in  )

    # NOTE: The bypass queue is required to prevent the simulation from
    # hanging. This bypass queue connects the memory response ports of the
    # bintree xcel to the response val-rdy bundle of the bintree lsq.
    # XXX: Need to investigate why
    s.byp_q = SingleElementBypassQueue( MemMsg(8,32,32).resp )

    s.connect( s.bintree_lsq.memresp_in, s.byp_q.enq )
    s.connect( s.bintree_hls.memresp,    s.byp_q.deq )

    # lsq <-> memreq/memresp
    s.connect( s.memreq,        s.bintree_lsq.memreq_out  )
    s.connect( s.memresp_q.deq, s.bintree_lsq.memresp_out )

    # commit port connections
    s.connect( s.commitreq_q.deq, s.bintree_lsq.commitreq  )
    s.connect( s.commitresp,      s.bintree_lsq.commitresp )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {}|({} {})|{} {}".format(
      s.xcelreq,
      s.xcelresp,
      s.commitreq,
      s.commitresp,
      s.memreq,
      s.memresp
    )
