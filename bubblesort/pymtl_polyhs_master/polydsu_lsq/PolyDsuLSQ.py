#=========================================================================
# PolyDsuLSQ
#=========================================================================
# Model implements a load-store queue that buffers the store requests from
# accelerators, handles commit requests from the processor, and handles the
# store-load forwarding.
#
# NOTE: incremental design strategy (ALL DONE):
#
#   1. I plan to first only support stores for accelerators that generate a
#   single memory request
#   2. Support the load requests without forwarding
#   3. Support the load requests with forwarding
#   4. Support accelerators that generate multiple load/store requests
#
#-------------------------------------------------------------------------
# Arbitration logic
#-------------------------------------------------------------------------
#
#   -------------------------------
#   Enqueue   Commit   Arbitrate?
#   -------------------------------
#   ld        drop     no
#   st        drop     no
#   ld        commit   yes
#   st        commit   no
#

from copy import deepcopy

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import RegEn
from pclib.rtl  import SingleElementBypassQueue

from StoreBuffer import StoreBuffer
from CommitMsg   import CommitReqMsg, CommitRespMsg

from xmem.MemMsgFuture   import MemMsg, MemReqMsg
from misc.PipeCtrlFuture import PipeCtrlFuture
from misc.Counter        import Counter

# XXX: Change funnel router model to not use the round-robin arbiter by
# default and allow the user to specify the arbiter to use. To allow loads
# have priority over pending commits.
from misc.FunnelRouter   import FunnelRouter

#-------------------------------------------------------------------------
# PolyDsuLSQ
#-------------------------------------------------------------------------

class PolyDsuLSQ( Model ):

  def __init__( s, num_entries ):

    addr_nbits    = clog2( num_entries )

    # NOTE: The number of entries has be be a power of two!
    s.num_entries = num_entries

    #---------------------------------------------------------------------
    # Interfaces
    #---------------------------------------------------------------------

    s.memreq_in   = InValRdyBundle  ( MemMsg(8,32,32).req   )
    s.memresp_in  = OutValRdyBundle ( MemMsg(8,32,32).resp  )

    s.commitreq   = InValRdyBundle   ( CommitReqMsg()  )
    s.commitresp  = OutValRdyBundle  ( CommitRespMsg() )

    s.memreq_out  = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.memresp_out = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    s.ldreq_out   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.ldresp_out  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    s.streq_out   = OutValRdyBundle ( MemMsg(8,32,32).req   )
    s.stresp_out  = InValRdyBundle  ( MemMsg(8,32,32).resp  )

    #---------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------

    s.squash          = Wire( 1 )
    s.advance_deq_ptr = Wire( addr_nbits )

    # queue to buffer the stores
    s.queue = StoreBuffer( num_entries, MemMsg(8, 32, 32).req )

    s.connect( s.queue.enq.msg, s.memreq_in.msg )
    s.connect( s.queue.deq.msg, s.streq_out.msg )

    s.connect( s.queue.squash,          s.squash          )
    s.connect( s.queue.advance_deq_ptr, s.advance_deq_ptr )

    #---------------------------------------------------------------------
    # enq0
    #---------------------------------------------------------------------
    # enqueue a store request and originate a stall if the queue is full

    s.do_enq  = Wire( 1 )
    s.sb_hit  = Wire( 1 )
    s.sb_addr = Wire( 10 )
    s.sb_data = Wire( 32 )

    s.dbg_opq = Wire( 8 )
    s.dbg_typ = Wire( 3 )

    @s.combinational
    def enq0():

      s.dbg_opq.value = s.memreq_in.msg.opaque
      s.dbg_typ.value = s.memreq_in.msg.type_

      # NOTE: Not synthesizeable RTL
      # search the store buffer and record the matching entry
      if s.memreq_in.msg.type_ == MemReqMsg.TYPE_READ and s.memreq_in.val:
        s.sb_hit.value  = 0
        s.sb_addr.value = 0
        s.sb_data.value = 0

        sb_ctrl  = s.queue.ctrl
        sb_dpath = s.queue.dpath
        # start the latest valid entry and break when a match is found
        if ~sb_ctrl.empty:
          i = deepcopy( sb_ctrl.enq_ptr ) - 1
          for x in range( s.num_entries ):
            if sb_dpath.queue.regs[ i ].addr == s.memreq_in.msg.addr:
              s.sb_hit.value  = 1
              s.sb_addr.value = i
              s.sb_data.value = sb_dpath.queue.regs[ i ].data
              break

            if   i == sb_ctrl.deq_ptr: break
            elif i == 0:               i = s.num_entries - 1
            else:                      i = i - 1

      else:
        s.sb_hit.value  = 0
        s.sb_addr.value = 0
        s.sb_data.value = 0


      # assign memreq_in.rdy
      if   s.memreq_in.msg.type_ == MemReqMsg.TYPE_WRITE:
        s.memreq_in.rdy.value = s.queue.enq.rdy & ~s.pipe_enq.prev_stall
      elif s.memreq_in.msg.type_ == MemReqMsg.TYPE_READ:
        if ~s.sb_hit:
          s.memreq_in.rdy.value = s.ldreq_out.rdy & ~s.pipe_enq.prev_stall
        else:
          s.memreq_in.rdy.value = 1
      else:
        s.memreq_in.rdy.value = 0

      # assign ldreq_out.val and ldreq_out.msg
      if s.memreq_in.msg.type_ == MemReqMsg.TYPE_READ:
        s.ldreq_out.val.value = s.memreq_in.val & ~s.sb_hit
        s.ldreq_out.msg.value = s.memreq_in.msg
      else:
        s.ldreq_out.val.value = 0
        s.ldreq_out.msg.value = 0

      # assign queue.enq_val
      if      s.memreq_in.msg.type_ == MemReqMsg.TYPE_WRITE:
        s.queue.enq.val.value = s.memreq_in.val & ~s.pipe_enq.prev_stall
      else:
        s.queue.enq.val.value = 0

      s.do_enq.value  = s.memreq_in.val & s.memreq_in.rdy

    #---------------------------------------------------------------------
    # Enqueue State
    #---------------------------------------------------------------------

    s.pipe_enq = PipeCtrlFuture()

    s.connect( s.pipe_enq.next_squash, 0        )
    s.connect( s.pipe_enq.next_stall,  0        )
    s.connect( s.pipe_enq.curr_squash, 0        )
    s.connect( s.pipe_enq.prev_val,    s.do_enq )

    s.memreq_in_msg  = RegEn( MemMsg(8,32,32).req )

    s.connect( s.memreq_in_msg.in_, s.memreq_in.msg        )
    s.connect( s.memreq_in_msg.en,  s.pipe_enq.curr_reg_en )

    s.sb_hit_reg = RegEn( 1 )

    s.connect( s.sb_hit_reg.in_, s.sb_hit               )
    s.connect( s.sb_hit_reg.en,  s.pipe_enq.curr_reg_en )

    s.sb_addr_reg = RegEn( 10 )

    s.connect( s.sb_addr_reg.in_, s.sb_addr              )
    s.connect( s.sb_addr_reg.en,  s.pipe_enq.curr_reg_en )

    s.sb_data_reg = RegEn( 32 )

    s.connect( s.sb_data_reg.in_, s.sb_data              )
    s.connect( s.sb_data_reg.en,  s.pipe_enq.curr_reg_en )

    @s.combinational
    def enq1():

      # assign pipe_enq.curr_stall
      if   s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_WRITE:
        s.pipe_enq.curr_stall.value  = ~s.memresp_in.rdy & s.pipe_enq.curr_val
      elif s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_READ:
        s.pipe_enq.curr_stall.value  = \
        ~s.sb_hit_reg.out & ( ~s.memresp_in.rdy | ~s.ldresp_out.val ) & s.pipe_enq.curr_val
      else:
        s.pipe_enq.curr_stall.value  = 0

      # assign ldresp_out.rdy
      if s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_READ:
        # do not assert ready to the memory until the accelerator is ready
        # to accept the memeory response value
        s.ldresp_out.rdy.value = s.pipe_enq.curr_val & s.memresp_in.rdy
      else:
        s.ldresp_out.rdy.value = 0

      # assign memresp_in.val
      if   s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_WRITE:
        s.memresp_in.val.value       = s.pipe_enq.curr_val
      elif s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_READ:
        if s.sb_hit_reg.out:
          s.memresp_in.val.value     = s.pipe_enq.curr_val
        else:
          s.memresp_in.val.value     = s.ldresp_out.val
      else:
        s.memresp_in.val.value     = s.pipe_enq.curr_val

      # assign memresp_in.msg
      if   s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_WRITE:
        s.memresp_in.msg.type_.value  = s.memreq_in_msg.out.type_
        s.memresp_in.msg.opaque.value = s.memreq_in_msg.out.opaque
        s.memresp_in.msg.len.value    = s.memreq_in_msg.out.len
        s.memresp_in.msg.data.value   = 0
      elif s.memreq_in_msg.out.type_ == MemReqMsg.TYPE_READ:
        s.memresp_in.msg.type_.value  = s.memreq_in_msg.out.type_
        s.memresp_in.msg.opaque.value = s.memreq_in_msg.out.opaque
        s.memresp_in.msg.len.value    = s.memreq_in_msg.out.len
        if ~s.sb_hit_reg.out:
          s.memresp_in.msg.data.value   = s.ldresp_out.msg.data
        else:
          s.memresp_in.msg.data.value   = s.sb_data_reg.out
      else:
        s.memresp_in.msg.value = 0

    #---------------------------------------------------------------------
    # commit0
    #---------------------------------------------------------------------
    # accept a commit request

    s.do_commit = Wire( 1 )

    s.streq_out_go  = Wire( 1 )
    s.stresp_out_go = Wire( 1 )

    # Counter that tracks the number of memory requests in flight
    s.inflight_memreqs = Counter( addr_nbits+1 )

    s.connect( s.inflight_memreqs.increment, s.streq_out_go  )
    s.connect( s.inflight_memreqs.decrement, s.stresp_out_go )

    @s.combinational
    def commit0():

      # logic that sets the value to advance the store buffer
      if ~s.pipe_commit.prev_stall & s.commitreq.val:
        s.squash.value = ~s.commitreq.msg.valid
      else:
        s.squash.value = 0

      # NOTE: Not synthesizeable RTL
      # logic that resets the deque pointer on a squash request
      if s.squash:
        sb_ctrl  = s.queue.ctrl
        sb_dpath = s.queue.dpath
        # start at the current position of the the deq_ptr and keep
        # updating the copy of the deq_ptr till we meet the enq_ptr as long
        # as the value of the opaque fields stored matches the sequence
        # number of the entry requested to be squashed
        i = deepcopy( sb_ctrl.deq_ptr )
        # iterate through all entries
        for x in range( s.num_entries ):
          # check if the stored entry and the sequence number match
          if sb_dpath.queue.regs[ i ].opaque == s.commitreq.msg.seq_num:
            if i == ( s.num_entries - 1 ): i = 0
            else:                          i = i + 1
            # break condition
            if ( i == sb_ctrl.enq_ptr ):
              break
        # the deq_ptr should be advance to this position
        s.advance_deq_ptr.value = i
      else:
        s.advance_deq_ptr.value = 0

      # assign queue.deq.rdy
      # NOTE: We dequeue when:
      #
      #   1. A new request to commit arrives and the previous stage is not
      #   stalling. In this case if we are squashing then we can dequeue
      #   right away else we need to make sure that the memory port is not
      #   busy.
      #   2. If a valid transaction later in the pipeline needs to update
      #   multiple memory locations in the memory then we deque till the
      #   tail message corresponds to a new sequence.
      s.queue.deq.rdy.value = \
      ( ( ~s.pipe_commit.prev_stall & s.commitreq.val
         & ( ~s.commitreq.msg.valid | ( s.commitreq.msg.valid & s.streq_out.rdy ) ) )
       | ( s.pipe_commit.curr_val & s.commit_msg_reg.out.valid & s.streq_out.rdy
           & ( s.queue.deq.msg.opaque == s.commit_msg_reg.out.seq_num ) )
      )

      # assign commitreq.rdy
      # NOTE: s.commitreq.rdy depends on s.commitreq.val
      s.commitreq.rdy.value = \
      (   ~s.pipe_commit.prev_stall & s.queue.deq.val & s.commitreq.val
        & ( ~s.commitreq.msg.valid | ( s.commitreq.msg.valid & s.streq_out.rdy ) )
      )

      # assign streq_out.val
      # NOTE: We assert valid when:
      #
      #   1. A new request to commit arrives and the previous stage is not
      #   stalling. In this case we assert a valid request to memory only
      #   if the message can commit. NOTE: I added a check to see if the value
      #   of the sequence number stored at the head is equal to the incoming
      #   request message sequence number for sanity.
      #
      #   2. If a valid transaction later in the pipeline needs to update
      #   multiple memory locations in the memory then we assert valid till
      #   the tail message corresponds to a new sequence.
      s.streq_out.val.value = \
      (   (  ~s.pipe_commit.prev_stall & s.queue.deq.val
            & s.commitreq.val
            & s.commitreq.msg.valid
            & ( s.queue.deq.msg.opaque == s.commitreq.msg.seq_num )
          )
        | (   s.pipe_commit.curr_val & s.commit_msg_reg.out.valid
            & ( s.queue.deq.msg.opaque == s.commit_msg_reg.out.seq_num )
            & s.queue.deq.val
          )
      )

      # assign do commit
      s.do_commit.value = s.commitreq.val & s.commitreq.rdy

      # assign the go signals for store request/responses
      s.streq_out_go.value = s.streq_out.val & s.streq_out.rdy
      s.stresp_out_go.value = s.stresp_out.val & s.stresp_out.rdy

    #---------------------------------------------------------------------
    # Commit State
    #---------------------------------------------------------------------

    s.pipe_commit = PipeCtrlFuture()

    s.connect( s.pipe_commit.next_squash, 0           )
    s.connect( s.pipe_commit.next_stall,  0           )
    s.connect( s.pipe_commit.curr_squash, 0           )
    s.connect( s.pipe_commit.prev_val,    s.do_commit )

    s.commit_msg_reg = RegEn( CommitReqMsg() )

    s.connect( s.commit_msg_reg.in_, s.commitreq.msg           )
    s.connect( s.commit_msg_reg.en,  s.pipe_commit.curr_reg_en )

    # Debug wires
    #s.dbg1 = Wire( 1 )
    #s.dbg2 = Wire( 8 )
    #s.dbg3 = Wire( 8 )
    #s.dbg4 = Wire( 1 )
    #s.dbg5 = Wire( 1 )

    @s.combinational
    def commit1():

      #s.dbg1.value = s.commit_msg_reg.out.valid
      #s.dbg2.value = s.commit_msg_reg.out.seq_num
      #s.dbg3.value = s.queue.deq.msg.opaque
      #s.dbg4.value = ( s.queue.deq.msg.opaque == s.commit_msg_reg.out.seq_num )
      #s.dbg5.value = ( s.commit_msg_reg.out.seq_num != s.queue.deq.msg.opaque )

      # assign stresp_out.rdy
      #
      # We assign the stresp_out.rdy signal if we have any store request that
      # is in flight
      s.stresp_out.rdy.value = \
      ( s.pipe_commit.curr_val & ~s.inflight_memreqs.count_is_zero )

      # assign commitresp.val
      #
      # Commit response valid is asserted when:
      # (a) If a squash request has updated state in the store buffer
      # (b) If the store buffer is completely drained and when all the acks are
      #     received
      # NOTE: The tricky case is when there is a single request in flight for
      # for which the ack is available and will be dequeued
      #
      # NOTE: squashes are guaranteed to be updated in one cycle.
      #
      # NOTE: 08-31-2015: fixed a bug in the store buffer drained check
      # logic where previously I only cared about the in flight requests to
      # be zero but had not considered if all the messages were indeed
      # dequeued -- indicated by the seq_num != queue.deq.msg.opaque
      #
      # NOTE: 09-03-2015: fixed one more bug! when the store buffer is
      # empty there could be garbage entries in the state that could match
      # the current sequence number we are draining for. I added a check
      # that considers the condition of when the queue is empty
      s.commitresp.val.value = \
      (  ( s.pipe_commit.curr_val & ~s.commit_msg_reg.out.valid )
       | ( s.pipe_commit.curr_val & s.commit_msg_reg.out.valid
           & s.inflight_memreqs.count_is_zero
           & (  ( s.commit_msg_reg.out.seq_num != s.queue.deq.msg.opaque )
              | s.queue.ctrl.empty )
         )
       | (   s.pipe_commit.curr_val & s.commit_msg_reg.out.valid
           & ( ( s.inflight_memreqs.count == 1 ) & s.stresp_out.val
           & (  ( s.commit_msg_reg.out.seq_num != s.queue.deq.msg.opaque )
              | s.queue.ctrl.empty ) )
         )
      )

      # assign stall
      #
      # Originate a stall if the commit response hasn't been sent out
      s.pipe_commit.curr_stall.value = \
        s.pipe_commit.curr_val & ( ~s.commitresp.rdy | ~s.commitresp.val )

      # assign commitresp.msg
      s.commitresp.msg.seq_num.value = s.commit_msg_reg.out.seq_num
      s.commitresp.msg.opaque.value  = s.commit_msg_reg.out.opaque
      s.commitresp.msg.xcel_id.value = s.commit_msg_reg.out.xcel_id

    #---------------------------------------------------------------------
    # FunnelRouter
    #---------------------------------------------------------------------

    # funnel Router for the memory ports
    s.mem_fr = FunnelRouter( 2, MemMsg(8,32,32).req, MemMsg(8,32,32).resp )

    # mem funnel connections
    s.connect( s.mem_fr.funnel_in[0], s.ldreq_out         )
    s.connect( s.mem_fr.funnel_in[1], s.streq_out         )
    s.connect( s.memreq_out,          s.mem_fr.funnel_out )

    # mem router connections
    s.connect( s.memresp_out,          s.mem_fr.router_in )
    s.connect( s.mem_fr.router_out[0], s.ldresp_out       )
    s.connect( s.mem_fr.router_out[1], s.stresp_out       )

