

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemReqMsg, MemRespMsg
from pclib.rtl  import RegRst, RegisterFile, NormalQueue, RoundRobinArbiter
from MapperMsg  import MapperReqMsg, MapperRespMsg
from ReducerMsg import ReducerReqMsg, ReducerRespMsg
from digitrecMsg import digitrecReqMsg, digitrecRespMsg

TYPE_READ = 0
TYPE_WRITE = 1

class SchedulerPRTL( Model ):

  def __init__( s, mapper_num = 10, reducer_num = 1):

    # Top Level Interface
    s.in_                 = InValRdyBundle  ( digitrecReqMsg() )
    s.out                 = OutValRdyBundle ( digitrecRespMsg() )
    s.reference           = InPort          ( 49 )
    s.base                = InPort          ( 32 )
    s.size                = InPort          ( 32 )

    # Global Memory Interface
    s.gmem_req            = OutValRdyBundle ( MemReqMsg(8, 32, 49) )
    s.gmem_resp           = InValRdyBundle  ( MemRespMsg(8, 49) )

    # Mapper Interface
    s.map_req             = OutValRdyBundle [mapper_num] ( MapperReqMsg() )
    s.map_resp            = InValRdyBundle  [mapper_num] ( MapperRespMsg() )

    # Reducer Interface
    s.red_req             = OutValRdyBundle [reducer_num] ( ReducerReqMsg() )
    s.red_resp            = InValRdyBundle [reducer_num] ( ReducerRespMsg() )

    # Task Queue
    s.task_queue          = NormalQueue ( mapper_num, MapperReqMsg() )

    # Idle Queue storing mapper ID
    s.idle_queue          = NormalQueue ( mapper_num, Bits(4) )

    # States
    s.STATE_IDLE   = 0    # Idle state, scheduler waiting for top level to start
    s.STATE_SOURCE = 1    # Source state, handling with Test Source, getting base, size, ref info
    s.STATE_INIT   = 2    # Init state, scheduler assigns input info to each Mapper
    s.STATE_START  = 3    # Start state, scheduler starts scheduling
    s.STATE_END    = 4    # End state, shceduler loads all task from global memory and it is done

    s.state          = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counters
    s.init_count     = Wire ( 2 )
    s.input_count    = Wire ( 32 )

    @s.tick
    def counter():
      if (s.idle_queue.enq.val and s.init):
        s.init_count.next = s.init_count + 1
      if (s.gmem_req.val):
        s.input_count.next = s.input_count + 1

    # Signals
    s.go             = Wire ( 1 ) # go signal tells scheduler to start scheduling
    s.mapper_done    = Wire ( 1 ) # if one or more mapper is done and send resp
    s.init           = Wire ( 1 ) # init signal indicates scheduler at initial state
    s.end            = Wire ( 1 ) # end signal indicates all task are loaded
    s.done           = Wire ( 1 ) # done signal indicates everything is done
    s.num_task_queue = Wire ( 2 )

    s.connect(s.task_queue.num_free_entries, s.num_task_queue)

    @s.combinational
    def logic():
      s.mapper_done.value = s.map_resp[0].val | s.map_resp[1].val | s.map_resp[2].val |
                            s.map_resp[3].val | s.map_resp[4].val | s.map_resp[5].val |
                            s.map_resp[6].val | s.map_resp[7].val | s.map_resp[8].val |
                            s.map_resp[9].val

    #---------------------------------------------------------------------
    # Assign Task to Mapper Combinational Logic
    #---------------------------------------------------------------------

    @s.combinational
    def mapper():

      # initialize mapper req and resp handshake signals
      for i in xrange(mapper_num):
        s.map_req[i].val.value = 0
      s.task_queue.deq.rdy.value = 0
      s.idle_queue.deq.rdy.value = 0

      if s.init:
      # mapper initialization, pass reference data to all mappers 1 by 1
        s.map_req[s.init_count].msg.data.value = s.reference
        s.map_req[s.init_count].msg.type_.value = 1
        s.map_req[s.init_count].val.value = 1
        s.idle_queue.enq.msg.value = s.init_count
        s.idle_queue.enq.val.value = 1
      else:
      # assign task to mapper if task queue is ready to dequeue
      # idle queue is ready to dequeue and mapper is ready to take request
        if (s.task_queue.deq.val and s.idle_queue.deq.val and
            s.map_req[s.idle_queue.deq.msg].rdy):
          s.map_req[s.idle_queue.deq.msg].msg.data.value  = s.task_queue.deq.msg.data
          s.map_req[s.idle_queue.deq.msg].msg.digit.value = s.task_queue.deq.msg.digit
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
      #s.idle_queue.enq.val.value = 0

      # get the mapper response, assign the response to reducer
      if (s.mapper_done):

        # Check each mapper response, add it to idle queue, send its response
        # to Reducer, mark its response ready
        for i in xrange(mapper_num):
          if(s.map_resp[i].val):
            s.map_resp[i].rdy.value = 1

            if ~s.init: # not a initialization mapper response
              if s.idle_queue.enq.rdy and s.red_req[0].rdy:
                s.idle_queue.enq.msg.value     = i
                s.idle_queue.enq.val.value     = 1
              # every computing is done
              if s.end and s.num_task_queue == mapper_num:
                s.done.value                   = 1
                s.red_req[0].msg.type_.value   = 2
              else:
                s.red_req[0].msg.type_.value   = 0
              s.red_req[0].msg.data.value    = s.map_resp[i].msg.data
              s.red_req[0].msg.digit.value   = s.map_resp[i].msg.digit
              s.red_req[0].val.value         = 1
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
        if ( s.go ):
          next_state = s.STATE_INIT
        elif ( s.done and s.red_resp[0].val):
          next_state = s.STATE_IDLE

      if ( curr_state == s.STATE_INIT ):
        if ( s.init_count == mapper_num-1 ):
          next_state = s.STATE_START

      if ( curr_state == s.STATE_START ):
        if ( s.input_count == s.size-1 ):
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

      current_state = s.state.out
      s.gmem_req.val.value = 0
      s.gmem_resp.rdy.value = 0
      s.in_.rdy.value = 0
      s.out.val.value = 0
      s.task_queue.enq.val.value = 0

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.init_count.value         = 0
        s.input_count.value        = 0
        s.end.value                = 0
        s.go.value                 = 0
        s.init.value               = 0
        s.done.value               = 0

      # In SOURCE state
      if (current_state == s.STATE_SOURCE):
        if (s.in_.val and s.out.rdy):
          if (s.in_.msg.type_ == digitrecReqMsg.TYPE_WRITE and
              s.red_req[0].rdy):
            if (s.in_.msg.addr == 0):   # start computing
              s.go.value                   = 1
            elif (s.in_.msg.addr == 1): # base address
              s.base.value                 = s.in_.msg.data
            elif (s.in_.msg.addr == 2): # size
              s.size.value                 = s.in_.msg.data
            elif (s.in_.msg.addr == 3): # reference data
              s.reference.value            = s.in_.msg.data
            elif (s.in_.msg.addr == 4): # local memory initialization
              s.red_req[0].msg.data.value  = 0
              s.red_req[0].msg.type_.value = 1 # ask reducer to start init process
              s.red_req[0].val.value       = 1
              
            # Send xcel response message
            s.in_.rdy.value           = 1
            s.out.msg.type_.value     = digitrecReqMsg.TYPE_WRITE
            s.out.msg.data.value      = 0
            s.out.val.value           = 1

          elif (s.in_.msg.type_ == digitrecReqMsg.TYPE_READ):
            # the computing is done, send response message
            if (s.done and s.red_resp[0].val):

              s.out.msg.type_.value     = digitrecReqMsg.TYPE_READ
              s.out.msg.data.value      = 1
              s.red_resp[0].rdy.value   = 1
              s.in_.rdy.value           = 1
              s.out.val.value           = 1

      # In INIT state
      if (current_state == s.STATE_INIT):

        s.init.value = 1
        s.go.value   = 0

        # at start of init, send read req to global memory
        if s.init_count == 0:
          if s.gmem_req.rdy:
            s.gmem_req.msg.addr.value  = s.base + (4 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value       = 1

        # at the rest of init, receive read resp to global memory, put it in task queue
        # send another read req to global memory
        else:
          if s.gmem_resp.val and s.gmem_req.rdy:
            s.task_queue.enq.msg.data.value = s.gmem_resp.msg
            s.task_queue.enq.msg.digit.value = s.input_count % 1800
            s.task_queue.enq.val.value = 1
            s.gmem_resp.rdy.value      = 1
            s.gmem_req.msg.addr.value  = s.base + (4 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value       = 1

      # In START state
      if (current_state == s.STATE_START):

        s.init.value = 0

        if s.gmem_resp.val and s.gmem_req.rdy:
          s.task_queue.enq.msg.data.value = s.gmem_resp.msg
          s.task_queue.enq.msg.digit.value = s.input_count % 1800
          s.task_queue.enq.val.value = 1
          s.gmem_resp.rdy.value = 1
          s.gmem_req.msg.addr.value = s.base + (4 * s.input_count)
          s.gmem_req.msg.type_.value = TYPE_READ
          s.gmem_req.val.value = 1

      # In END state
      if (current_state == s.STATE_END):
        if s.gmem_resp.val:
          s.task_queue.enq.msg.value = s.gmem_resp.msg
          s.task_queue.enq.val.value = 1
          s.gmem_resp.rdy.value = 1
          s.end.value = 1

  # Line Trace
  def line_trace( s ):

    state_str = "? "
    if s.state.out == s.STATE_IDLE:
      state_str = "IDLE"
    if s.state.out == s.STATE_SOURCE:
      state_str = "S   "
    if s.state.out == s.STATE_INIT:
      state_str = "INIT"
    if s.state.out == s.STATE_START:
      state_str = "ST  "
    if s.state.out == s.STATE_END:
      state_str = "END "

    return "( {}|m1:{}|m2:{}|r{}|g{}|{}|{}|{} )".format( state_str, s.map_req[0].val, 
                                    s.map_req[1].val, s.red_req[0].val,
                                    s.gmem_req.val, s.idle_queue.enq.val, s.num_task_queue, s.task_queue.deq.rdy)
