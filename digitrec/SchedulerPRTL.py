
import math

from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.ifcs  import MemReqMsg, MemRespMsg
from pclib.rtl   import RegRst, RegisterFile, NormalQueue, RoundRobinArbiter
from MapperMsg   import MapperReqMsg, MapperRespMsg
from ReducerMsg  import ReducerReqMsg, ReducerRespMsg
from digitrecMsg import digitrecReqMsg, digitrecRespMsg

TYPE_READ  = 0
TYPE_WRITE = 1
DATA_BITS  = 49
DIGIT      = 10
TRAIN_DATA = 1800

# import training data and store them into array
training_data = []
for i in xrange(DIGIT):
  filename = 'data/training_set_' + str(i) + '.dat'
  with open(filename, 'r') as f:
    for L in f:
      training_data.append(int(L.replace(',\n',''), 16))

class SchedulerPRTL( Model ):

  def __init__( s, mapper_num = 10, reducer_num = 1):

    # Top Level Interface
    s.in_                 = InValRdyBundle  ( digitrecReqMsg() )
    s.out                 = OutValRdyBundle ( digitrecRespMsg() )
    s.base                = InPort          ( 32 )
    s.size                = InPort          ( 32 )

    # Global Memory Interface
    s.gmem_req            = OutValRdyBundle ( MemReqMsg(8, 32, 56) )
    s.gmem_resp           = InValRdyBundle  ( MemRespMsg(8, 56) )

    # Register File Interface
    s.regf_addr           = Bits [DIGIT] ( 32 )
    s.regf_data           = Bits [DIGIT] ( DATA_BITS )
    s.regf_wren           = Bits [DIGIT] ( 1 )

    # Mapper Interface
    s.map_req             = OutValRdyBundle [mapper_num] ( MapperReqMsg() )
    s.map_resp            = InValRdyBundle  [mapper_num] ( MapperRespMsg() )

    # Reducer Interface
    s.red_req             = OutValRdyBundle [reducer_num] ( ReducerReqMsg() )
    s.red_resp            = InValRdyBundle  [reducer_num] ( ReducerRespMsg() )

    # States
    s.STATE_IDLE   = 0    # Idle state, scheduler waiting for top level to start
    s.STATE_SOURCE = 1    # Source state, handling with Test Source, getting base, size, ref info
    s.STATE_INIT   = 2    # Init state, scheduler assigns input info to each Mapper
    s.STATE_START  = 3    # Start state, scheduler gets test data, starts distributing and sorting
    s.STATE_READ   = 4    # Read state reads test data from global memory
    s.STATE_END    = 5    # End state, shceduler loads all task from global memory and it is done

    s.state          = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counters
    s.input_count    = Wire ( 32 )
    s.train_count_rd = Wire ( int( math.ceil( math.log( TRAIN_DATA, 2) ) ) )
    s.train_count_wr = Wire ( int( math.ceil( math.log( TRAIN_DATA, 2) ) ) )

    # Logic to Increment Counters
    @s.tick
    def counter():
      if (s.gmem_req.val):
        s.input_count.next = s.input_count + 1
      if (s.train_data_rd):
        if s.reset:
          s.train_count_rd.next = 0
        else:
          s.train_count_rd.next = s.train_count_rd + (mapper_num/DIGIT)
      if (s.train_data_wr):
        s.train_count_wr.next = s.train_count_wr + 1

    # Signals
    s.go             = Wire ( 1 ) # go signal tells scheduler to start scheduling
    s.end            = Wire ( 1 ) # end signal indicates all task are loaded
    s.done           = Wire ( 1 ) # done signal indicates everything is done
    s.reset          = Wire ( 1 ) # reset train count every test data processed

    #---------------------------------------------------------------------
    # Initialize Register File for Training data
    #---------------------------------------------------------------------

    @s.combinational
    def traindata():

      if s.train_data_wr:
        for i in xrange(DIGIT):
          s.regf_addr[i].value = s.train_count
          s.regf_data[i].value = training_data[i*1800 + s.train_count]
          s.regf_wren[i].value = 1
      else:
        for i in xrange(DIGIT):
          s.regf_wren[i].value = 0


    #---------------------------------------------------------------------
    # Assign Task to Mapper Combinational Logic
    #---------------------------------------------------------------------

    @s.combinational
    def mapper():

      # initialize mapper req and resp handshake signals
      for i in xrange(mapper_num):
        s.map_req[i].val.value = 0

      # broadcast train data to mapper
      for i in xrange(DIGIT):
        for j in xrange(mapper_num/DIGIT):
          if (s.map_req[j*10+i].rdy):
            s.map_req[j*10+i].msg.data.value    = 
            s.map_req[j*10+i].msg.address.value = s.train_count_rd + j
            s.map_req[j*10+i].msg.type_.value   = 0
            s.map_req[j*10+i].val.value         = 1

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
      for i in xrange(reducer_num):

        # send the msg to reducer only if all its corresponding mapper are done
        s.red_req[i].val.value = 1
        for j in xrange(mapper_num/reducer_num):
          if ~s.map_resp[j*10+i].val:
            s.red_req[i].val.value = 0

        # condition met, send reducer msg
        if s.red_req[i].val:

          # mark corresponding mapper response rdy
          for j in xrange(mapper_num/reducer_num):
            s.map_resp[j*10+i].rdy.value = 1

          # send reducer msg
          s.red_req[i].msg.data.value  = 
          s.red_req[i].msg.digit.value = 
          s.red_req[i].msg.type_.value = 

        # if this reducer response val, mark its rdy
        if ~s.done and s.red_resp[i].val:
          s.red_resp[i].rdy.value      = 1

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
        if ( s.train_count == TRAIN_DATA ):
          next_state = s.STATE_START

      if ( curr_state == s.STATE_START ):
        if ( s.train_count_rd == TRAIN_DATA):
          if ( s.input_count == s.size-1 ):
            next_state = s.STATE_END
          else:
            next_state = s.STATE_READ

      if ( curr_state == s.STATE_READ ):
        if ( s.gmem_req.val ):
          next_state = s.STATE_START

      if ( curr_state == s.STATE_END ):
        if ( s.done ):
          next_state = s.STATE_SOURCE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # Task State Output Logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_outputs():

      current_state          = s.state.out
      s.gmem_req.val.value   = 0
      s.gmem_resp.rdy.value  = 0
      s.in_.rdy.value        = 0
      s.out.val.value        = 0

      # In IDLE state
      if (current_state == s.STATE_IDLE):
        s.input_count.value        = 0
        s.train_count_rd.value     = 0
        s.train_count_wr.value     = 0
        s.end.value                = 0
        s.go.value                 = 0
        s.train_data_rd.value      = 0
        s.train_data_wr.value      = 0
        s.done.value               = 0
        s.reset.value              = 0

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

        s.train_data_wr.value = 1
        s.go.value            = 0

        # at the end of init, send read req to global memory
        if s.train_count_wr == TRAIN_DATA-1:
          if s.gmem_req.rdy:
            s.gmem_req.msg.addr.value  = s.base + (4 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value       = 1

      # In START state
      if (current_state == s.STATE_START):

        s.train_data_wr.value        = 0
        s.train_data_rd.value        = 1
        s.reset.value                = 0

        if s.train_count_rd == 0 and s.gmem_resp.val:
          s.gmem_resp.rdy.value      = 1
          s.reference.value          = s.gmem_resp.data

        if s.train_count_rd == TRAIN_DATA and s.gmem_req.rdy:
          s.gmem_req.msg.addr.value  = s.base + (4 * s.input_count)
          s.gmem_req.msg.type_.value = TYPE_READ
          s.gmem_req.val.value       = 1
          s.reset.value              = 1

      # In END state
      if (current_state == s.STATE_END):
        if s.gmem_resp.val:
          s.gmem_resp.rdy.value      = 1
          s.end.value                = 1

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

    return "( {}|{} )".format( state_str, s.init_count )
