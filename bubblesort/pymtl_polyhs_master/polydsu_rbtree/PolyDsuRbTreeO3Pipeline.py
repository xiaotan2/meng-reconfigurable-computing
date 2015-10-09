#=========================================================================
# PolyDsuRbTreeO3Pipeline
#=========================================================================
# This model puts together the PolyDSU and the LSQ unit to help drive the
# O3 integration. The model mocks up a send stage and a receive stage that
# interact with the PolyDSU and includes a Pipeline unit to emulate an O3
# pipeline. The send stage processes an incoming transaction and "sends" an
# iterator request message to the PolyDSU. The receive stage receives the
# response message from the PolyDSU and writes the result to a sink. The
# transaction from the receive stage is then inserted to the start of the
# Pipeline unit and once the transaction is available at the end of the
# pipeline unit the iterator-id is currently used to tell the LSQ to either
# commit or squash store updates.

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import SingleElementPipelinedQueue, RegEn
from pclib.rtl    import SingleElementBypassQueue

from PolyDsuRbTreeO3        import PolyDsuRbTreeO3

from polydsu_lsq.CommitMsg  import CommitReqMsg, CommitRespMsg
from polydsu.PolyDsuMsg     import PolyDsuReqMsg, PolyDsuRespMsg

from xmem.MemMsgFuture   import MemMsg
from misc.Pipeline       import Pipeline
from misc.PipeCtrlFuture import PipeCtrlFuture

#-------------------------------------------------------------------------
# PolyDsuRbTreeO3Pipeline
#-------------------------------------------------------------------------

class PolyDsuRbTreeO3Pipeline( Model ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.xcelreq  = InValRdyBundle  ( PolyDsuReqMsg()  )
    s.xcelresp = OutValRdyBundle ( PolyDsuRespMsg() )

    s.memreq   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    #---------------------------------------------------------------------
    # Models
    #---------------------------------------------------------------------

    # rbtree xcel
    s.rbtree_xcel = PolyDsuRbTreeO3()

    s.connect( s.rbtree_xcel.memreq,  s.memreq  )
    s.connect( s.rbtree_xcel.memresp, s.memresp )

    s.connect( s.rbtree_xcel.xcelreq.msg, s.xcelreq.msg )

    #---------------------------------------------------------------------
    # Send stage
    #---------------------------------------------------------------------
    # send the configuration message or the iterator message

    s.do_send = Wire( 1 )

    @s.combinational
    def send_request():

      s.rbtree_xcel.xcelreq.val.value = ~s.pipe_stg.prev_stall & s.xcelreq.val

      s.xcelreq.rdy.value = s.rbtree_xcel.xcelreq.rdy & ~s.pipe_stg.prev_stall

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

    s.connect( s.rbtree_xcel.xcelresp.msg, s.xcelresp.msg )

    @s.combinational
    def receive_response():

      # cannot assert the ready signal until the pipe can accept a transaction
      s.rbtree_xcel.xcelresp.rdy.value = s.pipe_stg.curr_val & s.xcelresp.rdy & s.pipe.in_.rdy

      # cannot assert the valid signal until the pipe can accept a transaction
      s.xcelresp.val.value = s.pipe_stg.curr_val & s.rbtree_xcel.xcelresp.val & s.pipe.in_.rdy

      s.pipe.in_.val.value = (   s.pipe_stg.curr_val
                               & s.xcelresp.val
                               & s.xcelresp.rdy )

      s.pipe_stg.curr_stall.value = \
        s.pipe_stg.curr_val & ( ~s.xcelresp.rdy
                              | ~s.rbtree_xcel.xcelresp.val
                              | ~s.pipe.in_.rdy
                              )

    #---------------------------------------------------------------------
    # inelastic pipeline
    #---------------------------------------------------------------------

    s.pipe = Pipeline( PolyDsuReqMsg(), 4 )

    s.connect( s.pipe.in_.msg, s.R_xcel_msg.out )

    #---------------------------------------------------------------------
    # Commit stage
    #---------------------------------------------------------------------

    @s.combinational
    def commit():

      # commit msg
      commit_msg       = Bits( 28, 0 )
      commit_msg[8:28] = 0
      commit_msg[8]    = s.pipe.out.msg[ PolyDsuReqMsg.iter_ ][0]
      commit_msg[0:8]  = s.pipe.out.msg.opq

      s.rbtree_xcel.commitreq.msg.value = commit_msg

      # commit request sent to the lsq only for stores
      if (   ( s.pipe.out.msg.opc == PolyDsuReqMsg.TYPE_SET )
          or ( s.pipe.out.msg.opc == PolyDsuReqMsg.TYPE_MFX ) ):
        s.rbtree_xcel.commitreq.val.value = s.pipe.out.val
        s.pipe.out.rdy.value            = s.rbtree_xcel.commitreq.rdy
      else:
        s.rbtree_xcel.commitreq.val.value = 0
        s.pipe.out.rdy.value              = 1

      # tie the value of the response to be 1 always
      s.rbtree_xcel.commitresp.rdy.value = 1

  #-----------------------------------------------------------------------
  # linetrace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return "{} {} | ( {} {} ) | {} {}".format(
      s.xcelreq,
      s.xcelresp,
      s.rbtree_xcel.commitreq,
      s.rbtree_xcel.commitresp,
      s.memreq,
      s.memresp
    )
