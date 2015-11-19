from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemReqMsg, MemRespMsg
from pclib.rtl  import RegRst, RegisterFile, NormalQueue, RoundRobinArbiter

TYPE_READ = 0
TYPE_WRITE = 1

class SchedulerPRLT( Model ):

  def __init__( s, mapper_num = 2, reducer_num = 1):

    # Top Level Interface
    s.in_ = InValRdyBundle ()
    s.out = InValRdyBundle ()

    # Global Memory Interface
    s.gmem_req  = InValRdyBundle ( MemReqMsg(8, 32, 32) )
    s.gmem_resp = InValRdyBundle ( MemRespMsg(8, 32) )

    # Local Memory Interface
    s.lmem_req  = InValRdyBundle ( MemReqMsg(8, 32, 32) )
    s.lmem_resp = InValRdyBundle ( MemRespMsg(8, 32) )

    # Mapper Interface
    s.map_req  = InValRdyBundle [mapper_num] ( MapperReqMessage() )
    s.map_resp = InValRdyBundle [mapper_num] ( MapperRespMessage() )

    # Reducer Interface
    s.red_req  = InValRdyBundle [reducer_num] ( ReducerReqMessage() )
    s.red_resp = InValRdyBundle [reducer_num] ( ReducerRespMessage() )

    # Task Queue
    s.task_queue = NormalQueue ( 2, Bits(32) )

    # Idle Queue storing mapper ID
    s.idle_queue = NormalQueue ( 2, Bits(2) )

    # States
    s.STATE_IDLE   = 0    # Idle state, scheduler waiting for top level to start
    s.STATE_INIT   = 1    # Init state, scheduler assigns input info to each Mapper
    s.STATE_MAP    = 2    # Map state, scheduler map task to mapper
    s.STATE_RED    = 3    # MapRed state, scheduler map task to mapper and call reducer to do work
    s.STATE_MAPRED = 4    # Red state, scheduler call reducer to work

    s.state       = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count  = Wire ( 2 )

    # Logic
    s.mapper_done = Wire ( 1 ) # if one or more mapper is done and send resp

    @s.combinational
    def logic():
      s.mapper_done.value = s.map_resp[0].val | s.map_resp[1].val
    

    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state    = s.state.out
      next_state    = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        if ( s.in_.val ):
          next_state = s.STATE_INIT

      if ( curr_state == s.STATE_INIT ):
        if ( s.init_count == mapper_num and
             s.gmem_req.rdy):
          next_state = s.STATE_MAP

      if ( curr_state == s.STATE_MAP ):

      if ( curr_state == s.STATE_MAPRED ):

      if ( curr_state == s.STATE_RED ):


    s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      currenti_state = s.state.out
      for i in xrange(mapper_num):
        s.map_req[i].val.value = 0
        s.map_resp[i].rdy.value = 0

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.init_count.value = 0

      # In INIT state
      if (current_state == s.STATE_INIT):

        # if mapper is rdy, send input info to mapper, and enq its id to idle queue
        if (s.init_count != mapper_num and s.map_req[s.init_count].rdy and
            s.idle_queue.enq.rdy):
          s.map_req[s.init_count].msg.value = 
          s.map_req[s.init_count].val.value = 1
          s.idle_queue.enq.msg.value = s.init_count
          s.idle_queue.enq.val.value = 1
          s.init_count.value = s.init_count + 1

        # at the last 2 cycle of init, send read req to global memory
        if s.init_count == mapper_num - 2:
          if s.gmem_req.rdy:
            s.gmem_req.msg.addr.value = 
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value = 1          

        # at the last cycle of init, receive read resp to global memory, put it in task queue
        if s.init_count == mapper_num - 1:
          if s.gmem_resp.val:
            s.task_queue.enq.msg.value = s.gmem_resp.msg
            s.task_queue.enq.val.value = 1
            s.gmem_resp.rdy.value = 1

      # In MAP state
      if (current_state == s.STATE_MAP):
        if (s.task_queue.deq.val and s.idle_queue.deq.val and
            s.map_req[s.idle_queue.deq.msg].rdy):
          s.map_req[s.idle_queue.deq.msg].msg.value = s.task_queue.deq.msg[0:8]
          s.map_req[s.idle_queue.deq.msg].val.value = 1
          s.task_queue.deq.rdy.value = 1
          s.idle_queue.deq.rdy.value = 1

      # In MAPRED state
      if (current_state == s.STATE_MAPRED):
        if (s.task_queue.deq.val and s.idle_queue.deq.val and s.idle_queue.enq.rdy and
            s.map_req[s.idle_queue.deq.msg].rdy and
            s.mapper_done and s.red_req.rdy):

          # Check each mapper response, add it to idle queue, send its response
          # to Reducer, mark its response ready
          for i in xrange(mapper_num):
            if(s.map_resp[i].val):
              s.idle_queue.enq.msg.value = i
              s.idle_queue.enq.val.value = 1
              s.red_req.msg.value = s.map_resp[i].msg
              s.red_req.val.value = 1
              s.map_resp[i].rdy.value = 1
              break

          # Send another mapper request
          s.map_req[s.idle_queue.deq.msg].msg.value = s.task_queue.deq.msg[0:8]
          s.map_req[s.idle_queue.deq.msg].val.value = 1
          s.task_queue.deq.rdy.value = 1
          s.idle_queue.deq.rdy.value = 1

      # In RED state
      if (current_state == s.STATE_RED):
        if ( s.idle_queue.enq.rdy and
             s.mapper_done and s.red_req.rdy ):
          # Check each mapper response, add it to idle queue, send its response
          # to Reducer, mark its response ready
          for i in xrange(mapper_num):
            if(s.map_resp[i].val):
              s.idle_queue.enq.msg.value = i
              s.idle_queue.enq.val.value = 1
              s.red_req.msg.value = s.map_resp[i].msg
              s.red_req.val.value = 1
              s.map_resp[i].rdy.value = 1
              break

