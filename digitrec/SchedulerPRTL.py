
import math

from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.ifcs  import MemReqMsg, MemRespMsg
from pclib.rtl   import Reg, RegRst, RegisterFile, NormalQueue, RoundRobinArbiter
from digitrecMsg import digitrecReqMsg, digitrecRespMsg

TYPE_READ  = 0
TYPE_WRITE = 1
DATA_BITS  = 49
DIGIT      = 10
DIGIT_LOG  = int(math.ceil(math.log(DIGIT, 2)))
TRAIN_DATA = 6
TRAIN_LOG  = int(math.ceil(math.log(TRAIN_DATA, 2)))
TEST_DATA  = 180
TEST_LOG   = int(math.ceil(math.log(TEST_DATA, 2)))

# import training data and store them into array
training_data = []
count = 0
for i in xrange(DIGIT):
  filename = 'data/training_set_' + str(i) + '.dat'
  with open(filename, 'r') as f:
    for L in f:
      if(count > TRAIN_DATA):
        break;
      training_data.append(int(L.replace(',\n',''), 16))
      count = count + 1

class SchedulerPRTL( Model ):

  def __init__( s, mapper_num = 10, reducer_num = 1):

    # Top Level Interface
    s.in_                 = InValRdyBundle  ( digitrecReqMsg() )
    s.out                 = OutValRdyBundle ( digitrecRespMsg() )
    s.base                = InPort          ( 32 )
    s.size                = InPort          ( 32 )

    # Global Memory Interface
    s.gmem_req            = OutValRdyBundle ( MemReqMsg(8, 32, 64) )
    s.gmem_resp           = InValRdyBundle  ( MemRespMsg(8, 64) )

    # Register File Interface
    s.regf_addr           = OutPort [DIGIT] ( TRAIN_LOG )
    s.regf_data           = OutPort [DIGIT] ( DATA_BITS )
    s.regf_wren           = OutPort [DIGIT] ( 1 )
    s.regf_rdaddr         = OutPort [mapper_num] ( TRAIN_LOG )

    # Mapper Interface
    s.map_req             = OutPort [mapper_num] ( DATA_BITS )

    # Reducer Reset
    s.red_rst             = OutPort ( 1 )

    # Merger Interface
    s.merger_resp         = InPort ( DIGIT_LOG )

    # States
    s.STATE_IDLE   = 0    # Idle state, scheduler waiting for top level to start
    s.STATE_SOURCE = 1    # Source state, handling with Test Source, getting base, size, ref info
    s.STATE_INIT   = 2    # Init state, scheduler assigns input info to each Mapper
    s.STATE_START  = 3    # Start state, scheduler gets test data, starts distributing and sorting
    s.STATE_WRITE  = 4    # Write state, scheduler writes merger data to memory
    s.STATE_END    = 5    # End state, shceduler loads all task from global memory and it is done

    s.state          = RegRst( 4, reset_value = s.STATE_IDLE )

    # Counters
    s.input_count    = Wire ( TEST_LOG )
    s.result_count   = Wire ( TEST_LOG )
    s.train_count_rd = Wire ( TRAIN_LOG )
    s.train_count_wr = Wire ( TRAIN_LOG )
    s.train_data_wr  = Wire ( 1 )
    s.train_data_rd  = Wire ( 1 )


    # Logic to Increment Counters
    @s.tick
    def counter():

      if (s.gmem_req.val and s.gmem_req.msg.type_ == TYPE_READ):
        s.input_count.next = s.input_count + 1

      if (s.gmem_req.val and s.gmem_req.msg.type_ == TYPE_WRITE):
        s.result_count.next = s.result_count + 1

      if s.rst:
        s.train_count_rd.next = 0
      elif s.train_data_rd:
        s.train_count_rd.next = s.train_count_rd + (mapper_num/DIGIT)

      if (s.train_data_wr):
        s.train_count_wr.next = s.train_count_wr + 1

    # Signals
    s.go             = Wire ( 1 ) # go signal tells scheduler to start scheduling
    s.done           = Wire ( 1 ) # done signal indicates everything is done
    s.rst            = Wire ( 1 ) # reset train count every test data processed

    # Reference data
    s.reference      = Reg(dtype=DATA_BITS)      # reference stores test data

    #---------------------------------------------------------------------
    # Initialize Register File for Training data
    #---------------------------------------------------------------------

    @s.combinational
    def traindata():

      if s.train_data_wr:
        for i in xrange(DIGIT):
          s.regf_addr[i].value = s.train_count_wr
          s.regf_data[i].value = training_data[i*1800 + s.train_count_wr]
          s.regf_wren[i].value = 1
      else:
        for i in xrange(DIGIT):
          s.regf_wren[i].value = 0


    #---------------------------------------------------------------------
    # Assign Task to Mapper Combinational Logic
    #---------------------------------------------------------------------

    @s.combinational
    def mapper():

      # broadcast train data to mapper
      for i in xrange(DIGIT):
        for j in xrange(mapper_num/DIGIT):
          if (s.train_data_rd):
            s.map_req[j*10+i].value             = s.reference.out
            s.regf_rdaddr[j*10+i].value         = s.train_count_rd + j

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
        elif ( s.done ):
          next_state = s.STATE_IDLE

      if ( curr_state == s.STATE_INIT ):
        if ( s.train_count_wr == TRAIN_DATA-1 ):
          next_state = s.STATE_START

      if ( curr_state == s.STATE_START ):
        if ( s.train_count_rd == TRAIN_DATA-3 ):
          next_state = s.STATE_WRITE

      if ( curr_state == s.STATE_WRITE ):
        if ( s.input_count == s.size ):
          next_state = s.STATE_END
        else:
          next_state = s.STATE_START

      if ( curr_state == s.STATE_END ):
        if s.gmem_resp.val:
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
        s.reference.value          = 0
        s.go.value                 = 0
        s.train_data_rd.value      = 0
        s.train_data_wr.value      = 0
        s.done.value               = 0
        s.rst.value                = 0
        s.red_rst.value            = 0

      # In SOURCE state
      if (current_state == s.STATE_SOURCE):
        if (s.in_.val and s.out.rdy):
          if (s.in_.msg.type_ == digitrecReqMsg.TYPE_WRITE):
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
            if (s.done):

              s.out.msg.type_.value     = digitrecReqMsg.TYPE_READ
              s.out.msg.data.value      = 1
              s.in_.rdy.value           = 1
              s.out.val.value           = 1

      # In INIT state
      if (current_state == s.STATE_INIT):

        s.train_data_wr.value = 1
        s.go.value            = 0

        # at the end of init, send read req to global memory
        if s.train_count_wr == TRAIN_DATA-1:
          if s.gmem_req.rdy:
            s.gmem_req.msg.addr.value  = s.base + (8 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value       = 1
            s.red_rst.value            = 1

      # In START state
      if (current_state == s.STATE_START):

        s.train_data_wr.value        = 0
        s.train_data_rd.value        = 1
        s.rst.value                  = 0
        s.red_rst.value              = 0

        if s.gmem_resp.val:
        # if response type is read, stores test data to reference, hold response val
        # until everything is done, which is set in WRITE state
          if s.gmem_resp.msg.type_ == TYPE_READ:
            s.gmem_resp.rdy.value      = 1
            s.reference.in_.value      = s.gmem_resp.msg.data
          else:
        # if response tyle is write, set response rdy, send another req to
        # read test data
            s.gmem_resp.rdy.value      = 1
            s.gmem_req.msg.addr.value  = s.base + (8 * s.input_count)
            s.gmem_req.msg.type_.value = TYPE_READ
            s.gmem_req.val.value       = 1
            s.red_rst.value            = 1

      # In WRITE state
      if (current_state == s.STATE_WRITE):

        s.train_data_rd.value        = 0
        # one test data done processed, write result from merger to memory
        if ( s.gmem_req.rdy ):
          s.gmem_req.msg.addr.value  = 0x2000 + (8 * s.result_count)
          s.gmem_req.msg.data.value  = s.merger_resp
          s.gmem_req.msg.type_.value = TYPE_WRITE
          s.gmem_req.val.value       = 1
          s.rst.value                = 1

      # In END state
      if (current_state == s.STATE_END):
        if s.gmem_resp.val:
          s.gmem_resp.rdy.value      = 1
          s.done.value               = 1

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
    if s.state.out == s.STATE_WRITE:
      state_str = "WRI "
    if s.state.out == s.STATE_END:
      state_str = "END "

    return "( {}|{}|{}|{}|{}|{} )".format( state_str, s.input_count, s.train_count_rd,
                                   s.regf_rdaddr[0], s.gmem_resp.msg.data, s.merger_resp )
