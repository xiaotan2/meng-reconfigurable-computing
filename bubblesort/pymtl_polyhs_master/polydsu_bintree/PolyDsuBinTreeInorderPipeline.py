#=========================================================================
# PolyDsuBinTreeInorderPipeline
#=========================================================================
# This model mocks up a send stage and a receive stage that interact with the
# iterator translation unit. The send stage processes an incoming transaction
# and "sends" either a configuration message request or a iterator message to
# the Xcel. The receive stage receives the response message from the Xcel and
# writes the result to a sink. The model assumes that the send stage is
# connected to two sources at the start of the pipeline and two sinks at the
# end of the pipeline

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import SingleElementPipelinedQueue, RegEn

from PolyDsuBinTree      import PolyDsuBinTree

from xmem.MemMsgFuture  import MemMsg
from polydsu.PolyDsuMsg import PolyDsuReqMsg, PolyDsuRespMsg

from misc.PipeCtrlFuture import PipeCtrlFuture

#-------------------------------------------------------------------------
# PolyDsuBinTreeInorderPipeline
#-------------------------------------------------------------------------

class PolyDsuBinTreeInorderPipeline( Model ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq  = InValRdyBundle  ( PolyDsuReqMsg()  )
    s.xcelresp = OutValRdyBundle ( PolyDsuRespMsg() )

    s.memreq   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    #---------------------------------------------------------------------
    # BinTree Xcel
    #---------------------------------------------------------------------

    s.bintree_xcel = PolyDsuBinTree()

    s.connect( s.bintree_xcel.memreq,  s.memreq  )
    s.connect( s.bintree_xcel.memresp, s.memresp )

    s.connect( s.bintree_xcel.xcelreq.msg, s.xcelreq.msg )

    #---------------------------------------------------------------------
    # Send stage
    #---------------------------------------------------------------------
    # send the configuration message or the iterator message

    s.do_send = Wire( 1 )

    @s.combinational
    def send_request():

      s.bintree_xcel.xcelreq.val.value = ~s.pipe_stg.prev_stall & s.xcelreq.val

      s.xcelreq.rdy.value = s.bintree_xcel.xcelreq.rdy & ~s.pipe_stg.prev_stall

      s.do_send.value = s.xcelreq.val & s.xcelreq.rdy

    #---------------------------------------------------------------------
    # Receive stage
    #---------------------------------------------------------------------
    # receive response messages

    s.pipe_stg = PipeCtrlFuture()

    s.connect( s.pipe_stg.next_squash, 0 )
    s.connect( s.pipe_stg.next_stall,  0 )
    s.connect( s.pipe_stg.curr_squash, 0 )

    s.connect( s.pipe_stg.prev_val, s.do_send )

    s.R_xcel_msg = RegEn( PolyDsuReqMsg() )

    s.connect( s.xcelreq.msg,          s.R_xcel_msg.in_ )
    s.connect( s.pipe_stg.curr_reg_en, s.R_xcel_msg.en  )

    s.connect( s.bintree_xcel.xcelresp.msg, s.xcelresp.msg )

    @s.combinational
    def receive_response():

      s.bintree_xcel.xcelresp.rdy.value = s.pipe_stg.curr_val & s.xcelresp.rdy

      s.xcelresp.val.value = s.pipe_stg.curr_val & s.bintree_xcel.xcelresp.val

      s.pipe_stg.curr_stall.value = \
        s.pipe_stg.curr_val & ( ~s.xcelresp.rdy | ~s.bintree_xcel.xcelresp.val )

  #-----------------------------------------------------------------------
  # linetrace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} | {} {}".format(
      s.bintree_xcel.xcelreq,
      s.bintree_xcel.xcelresp,
      s.memreq,
      s.memresp
    )
