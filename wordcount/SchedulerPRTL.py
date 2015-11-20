

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemReqMsg, MemRespMsg
from pclib.rtl  import RegRst, RegisterFile, NormalQueue, RoundRobinArbiter
from MapperMsg  import MapperReqMsg, MapperRespMsg
from ReducerMsg import ReducerReqMsg, ReducerRespMsg
from WordcountMsg import WordcountReqMsg, WordcountRespMsg

TYPE_READ = 0
TYPE_WRITE = 1

class SchedulerPRLT( Model ):

  def __init__( s, mapper_num = 2, reducer_num = 1):

    # Top Level Interface
    s.in_ = InValRdyBundle  ( WordcountReqMsg() )
    s.out = OutValRdyBundle ( WordcountRespMsg() )
    s.referece = InPort ( 32 )
    s.base     = InPort ( 32 )
    s.size     = InPort ( 32 )

    # Global Memory Interface
    s.gmem_req  = OutValRdyBundle ( MemReqMsg(8, 32, 32) )
    s.gmem_resp = InValRdyBundle ( MemRespMsg(8, 32) )

    # Local Memory Interface
    s.lmem_req  = OutValRdyBundle ( MemReqMsg(8, 32, 32) )
    s.lmem_resp = InValRdyBundle ( MemRespMsg(8, 32) )

    # Mapper Interface
    s.map_req  = OutValRdyBundle [mapper_num] ( MapperReqMsg() )
    s.map_resp = InValRdyBundle [mapper_num] ( MapperRespMsg() )

    # Reducer Interface
    s.red_req  = OutValRdyBundle [reducer_num] ( ReducerReqMsg() )
    s.red_resp = InValRdyBundle [reducer_num] ( ReducerRespMsg() )

    # Task Queue
    s.task_queue = NormalQueue ( 2, Bits(32) )

    # Idle Queue storing mapper ID
    s.idle_queue = NormalQueue ( 2, Bits(2) )

    # States
    s.STATE_IDLE   = 0    # Idle state, scheduler waiting for top level to start
    s.STATE_SOURCE = 1    # Source state, handling with Test Source, getting base, size, ref info
    s.STATE_INIT   = 2    # Init state, scheduler assigns input info to each Mapper
    s.STATE_START  = 3    # Start state, scheduler starts scheduling
    s.STATE_END    = 4    # End state, shceduler loads all task from global memory and it is done

    s.state       = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count     = Wire ( 2 )
    s.input_count    = Wire ( 32 )

    # Signals
    s.go             = Wire ( 1 ) # go signal tells scheduler to start scheduling
    s.mapper_done    = Wire ( 1 ) # if one or more mapper is done and send resp
    s.init           = Wire ( 1 ) # init signal indicates scheduler at initial state
    s.end            = Wire ( 1 ) # end signal indicates all task are loaded
    s.num_task_queue = Wire ( 2 )

    s.connect(s.task_queue.num_free_entries, s.num_task_queue)

    @s.combinational
    def logic():
      s.mapper_done.value = s.map_resp[0].val | s.map_resp[1].val

    #---------------------------------------------------------------------
    # Assign Task to Mapper Combinational Logic
    #---------------------------------------------------------------------

    @s.combinational
    def mapper():

      # initialize mapper req and resp handshake signals
      for i in xrange(mapper_num):
        s.map_req[i].val.value = 0

      if ~s.init:
      # assign task to mapper if task queue is ready to dequeue
      # idle queue is ready to dequeue and mapper is ready to take request
        if (s.task_queue.deq.val and s.idle_queue.deq.val and
            s.map_req[s.idle_queue.deq.msg].rdy):
          s.map_req[s.idle_queue.deq.msg].msg.data.value = s.task_queue.deq.msg[0:8]
          s.map_req[s.idle_queue.deq.msg].msg.type_.value = 0
          s.map_req[s.idle_queue.deq.msg].val.value = 1
          s.task_queue.deq.rdy.value = 1
          s.idle_queue.deq.rdy.value = 1
    
    #---------------------------------------------------------------------
    # Send Mapper Resp to Reducer Combinational Logic
    #---------------------------------------------------------------------

    @s.combinational
    def reducer():

      # initialize mapper and reducer handshake signals
      for i in xrange(mapper_num):
        s.map_resp[i].rdy.value = 0
      for i in xrange(reducer_num):
        s.red_req[i].val.value = 0

      # get the mapper response, assign the response to reducer
      if (s.idle_queue.enq.rdy and
          s.mapper_done and s.red_req.rdy):

        # Check each mapper response, add it to idle queue, send its response
        # to Reducer, mark its response ready
        for i in xrange(mapper_num):
          if(s.map_resp[i].val):
            s.idle_queue.enq.msg.value = i
            s.idle_queue.enq.val.value = 1
            if s.end and s.num_task_queue == 0:
              s.red_req.msg.data.value = s.map_resp[i].msg.data
              s.red_req.msg.type_.value = 1
              s.red_req.val.value = 1
              s.map_resp[i].rdy.value = 1
              s.done.value = 1
            else:
              s.red_req.msg.data.value = s.map_resp[i].msg.data
              s.red_req.msg.type_.value = 0
              s.red_req.val.value = 1
              s.map_resp[i].rdy.value = 1
            break

    #---------------------------------------------------------------------
    # Task State Transition Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state    = s.state.out
      next_state    = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        if ( s.in_.val ):
          next_state = s.STATE_SOURCE

      if ( curr_state == s.STATE_SOURCE ):
        if ( s.init_count == mapper_num ):
          next_state = s.STATE_INIT

      if ( curr_state == s.STATE_INIT ):
        if ( s.init_count == mapper_num ):
          next_state = s.STATE_START

      if ( curr_state == s.STATE_START ):
        if ( s.input_counti == s.size ):
          next_state = s.STATE_END

      if ( curr_state == s.STATE_END ):
        if ( s.done ):
          next_state = s.STATE_SOURCE

    s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # Task State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      currenti_state = s.state.out
      s.gmem_req.val.value = 0
      s.gmem_resp.rdy.value = 0

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.init_count.value = 0
        s.input_count.value = 0
        s.end.value = 0
        s.init.value = 0
        s.done.value = 0
        if s.in_.val:
          s.in_.rdy.value = 1

      #In SOURCE state
      if (current_state == s.STATE_SOURCE):
        if (s.in_.val and s.out.rdy):
          if (s.in_.msg.type_ == WordcountReqMsg.TYPE_WRITE):
            if (s.in_.msg.addr == 0):
              s.go.value      = 1
            elif (s.in_.msg.addr == 1):
              s.base.value               = s.in_.msg.data
            elif (s.in_.msg.addr == 2):
              s.size.value               = s.in_.msg.data
            elif (s.in_.msg.addr == 3):
              s.reference.value          = s.in_.msg.data
            # Send xcel response message
            s.in_.rdy.value           = 1
            s.out.msg.type_.value     = WordcountReqMsg.TYPE_WRITE
            s.out.msg.data.value      = 0
            s.out.val.value           = 1

          elif (s.in_.msg.type_ == WordcountReqMsg.TYPE_READ):
            s.out.msg.type_.value     = WordcountReqMsg.TYPE_READ
            s.out.msg.data.value      = s.red_resp.msg.data
            s.done.value              = 0
            s.in_.rdy.value           = 1
            s.out.val.value           = 1

      # In INIT state
      if (current_state == s.STATE_INIT):

        s.init.value = 1

        # if mapper is rdy, send input info to mapper, and enq its id to idle queue
        if (s.init_count != mapper_num and s.map_req[s.init_count].rdy and
            s.idle_queue.enq.rdy):
          s.map_req[s.init_count].msg.data.value = s.reference
          s.map_req[s.init_count].msg.type_.value = 1
          s.map_req[s.init_count].val.value = 1
          s.idle_queue.enq.msg.value = s.init_count
          s.idle_queue.enq.val.value = 1
          s.init_count.value = s.init_count + 1

        # at the last 2 cycle of init, send read req to global memory
        if s.init_count == mapper_num - 2:
          if s.gmem_req.rdy:
            s.gmem_req.msg.addr.value = s.base + (4 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value = 1
            s.input_count = s.input_count + 1

        # at the last cycle of init, receive read resp to global memory, put it in task queue
        # send another read req to global memory
        if s.init_count == mapper_num - 1:
          if s.gmem_resp.val and s.gmem_req.rdy:
            s.task_queue.enq.msg.value = s.gmem_resp.msg
            s.task_queue.enq.val.value = 1
            s.gmem_resp.rdy.value = 1
            s.gmem_req.msg.addr.value = s.base + (4 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value = 1
            s.input_count = s.input_count + 1

      # In START state
      if (current_state == s.STATE_START):

        s.init.value = 0

        if s.gmem_resp.val and s.gmem_req.rdy:
          s.task_queue.enq.msg.value = s.gmem_resp.msg
          s.task_queue.enq.val.value = 1
          s.gmem_resp.rdy.value = 1
          s.gmem_req.msg.addr.value = s.base + (4 * s.input_count)
          s.gmem_req.msg.type_.value = TYPE_READ
          s.gmem_req.val.value = 1
          s.input_count = s.input_count + 1

      # In END state
      if (current_state == s.STATE_END):
        if s.gmem_resp.val:
          s.task_queue.enq.msg.value = s.gmem_resp.msg
          s.task_queue.enq.val.value = 1
          s.gmem_resp.rdy.value = 1
          s.end.value = 1

