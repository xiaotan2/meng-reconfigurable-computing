#=========================================================================
# PageRank RTL Test Framework
#=========================================================================

import pytest
import random
import struct

from pymtl           import *
from pclib.test      import mk_test_case_table, run_sim
from pclib.test      import TestSource, TestSink
from pclib.test      import TestMemory
from pclib.ifcs      import MemMsg, MemReqMsg, MemRespMsg

from SchedulerVRTL_alt  import SchedulerVRTL_alt
from pageRankMsg     import pageRankReqMsg, pageRankRespMsg

from numpy           import dot, transpose

#-------------------------------------------------------------------------
# Parameters. User can modify parameters here
#-------------------------------------------------------------------------

TEST_SIZE   = 180
TRAIN_SIZE  = 1800
MAPPER_NUM  = 30
REDUCER_NUM = 10 
k           = 3
MAX_CYCLES  = 80

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, SchedulerVRTL, src_msgs, sink_msgs,
               stall_prob, latency, src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src       = TestSource    ( pageRankReqMsg(),  src_msgs,  src_delay  )
    s.di        = SchedulerVRTL
    s.sink      = TestSink      ( pageRankRespMsg(), sink_msgs, sink_delay )
    s.mem       = TestMemory    ( MemMsg(8,32,32), 1, stall_prob, latency   )

    # Dump VCD
    if dump_vcd:
      s.di.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.di = TranslationTool( s.di )

    # Connect
    s.connect( s.src.out,              s.di.direq        )
    s.connect( s.di.diresp,            s.sink.in_        )
    s.connect( s.di.memreq,            s.mem.reqs[0]     )
    s.connect( s.di.memresp,           s.mem.resps[0]    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
#    return  s.di.line_trace() + " > " + s.mem.line_trace() + ">" + s.sink.line_trace()
    return s.src.line_trace() + ">" + s.di.line_trace() + ">" + s.mem.line_trace() + ">" + s.sink.line_trace()
#s.src.line_trace()       + " > " + \
#           s.di.line_trace(mapper_num=30, reducer_num=10) + " > " + \
#           s.sink.line_trace()    


#-------------------------------------------------------------------------
# make msgs
#-------------------------------------------------------------------------

def req( type, addr, data ):
  msg      = pageRankReqMsg()
  if type == 'rd': msg.type_ = pageRankReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = pageRankReqMsg.TYPE_WRITE
  msg.addr = addr
  msg.data = data
  return msg

def resp( type, data ):
  msg      = pageRankRespMsg()
  if type == 'rd': msg.type_ = pageRankReqMsg.TYPE_READ
  if type == 'wr': msg.type_ = pageRankReqMsg.TYPE_WRITE
  msg.data = data
  return msg
  
#-------------------------------------------------------------------------
# Protocol 
#-------------------------------------------------------------------------

def gen_protocol_msgs( size, result, runs ):
  return [
    req( 'wr', 1, 0x1000 ), resp( 'wr', 0      ),
    req( 'wr', 2, 0x2000 ), resp( 'wr', 0      ),
    req( 'wr', 3, size   ), resp( 'wr', 0      ),
    req( 'wr', 4, runs   ), resp( 'wr', 0      ),
    req( 'wr', 0, 0      ), resp( 'wr', 0      ),
    req( 'rd', 0, 0      ), resp( 'rd', result ),
  ]


#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------
# convert n^2 vector into nxn matrix
def vectorToMatrix(vector, length):
  matrix = []
  for i in xrange(length):
    matrix.append([])
  for i in xrange(len(vector)):
    matrix[i/length].append(vector[i])
  return matrix

# convert nxn matrix into n^2 vector
def matrixToVector(matrix, length):
  vector = []
  for i in xrange(len(matrix)):
    for j in xrange(len(matrix[i])):
      vector.append(matrix[i][j])
  return vector

# combine 4 data into 1
def fourElementsToOne(data):
  list_t = []
  counter = 0
  data_t = 0
  for i in xrange(len(data)):
    if counter == 4:
      list_t.append(data_t)
      data_t = data[i]
      counter = 1
    else:
      data_t = (data_t << 8) + data[i]
      counter += 1
  if counter == 4:
    list_t.append(data_t)
  return list_t

random.seed()

# vector R
vectorR_1run = []
for i in xrange(8):
  vectorR_1run.append(random.randint(1,10))

# test data 8x8 matrix with 1 run
test_8data_1run = []
result_8data_1run = []
for i in xrange(8):
  for j in xrange(8):
    test_8data_1run.append(random.randint(1,10))

vectorR_4run = []
for i in xrange(8):
  vectorR_4run.append(random.randint(0,2))

test_8data_4run = []
result_8data_4run = []
for i in xrange(8):
  for j in xrange(8):
    test_8data_4run.append(random.randint(0,2))

result_8data_1run = dot(vectorR_1run, vectorToMatrix(test_8data_1run, 8))
result_8data_4run = dot(vectorR_4run, vectorToMatrix(test_8data_4run, 8))
for i in xrange(3):
  result_8data_4run = dot(result_8data_4run, vectorToMatrix(test_8data_4run, 8))

matrix_test = vectorToMatrix(test_8data_1run, 8)
matrix_test = transpose(matrix_test)
test_8data_1run = matrixToVector(matrix_test, 8)

matrix_test = vectorToMatrix(test_8data_4run, 8)
matrix_test = transpose(matrix_test)
test_8data_4run = matrixToVector(matrix_test, 8)

test_8data_1run = fourElementsToOne(test_8data_1run)
result_8data_1run = fourElementsToOne(result_8data_1run)
vectorR_1run = fourElementsToOne(vectorR_1run)

test_8data_4run = fourElementsToOne(test_8data_4run)
result_8data_4run = fourElementsToOne(result_8data_4run)
vectorR_4run = fourElementsToOne(vectorR_4run)

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------
test_case_table = mk_test_case_table([
  (                       "matrixG            vectorR      result   runs   stall  latency  src_delay  sink_delay" ),
  [ "test8_1_0x0x0",    test_8data_1run,    vectorR_1run,    1,      1,      0,     0,       0,         0         ],
  [ "test8_2_0x0x0",    test_8data_1run,    vectorR_1run,    1,      2,      0,     0,       0,         0         ],
  [ "test8_3_0x0x0",    test_8data_1run,    vectorR_1run,    1,      3,      0,     0,       0,         0         ],
#  [ "test8_4_0x0x0",    test_8data_4run,    vectorR_4run,    1,      4,      0,     0,       0,         0         ],
#  [ "test8_delay",    test_8data,    vectorR,    1,         0.3,     3,       2,         3         ],
])

#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( pageRank, test_params, dump_vcd, test_verilog=False ):

  G_data       = test_params.matrixG
  result       = test_params.result
  R_data       = test_params.vectorR
  runs         = test_params.runs
  G_data_bytes = struct.pack("<{}L".format(len(G_data)), *G_data)
  R_data_bytes = struct.pack("<{}L".format(len(R_data)), *R_data)
  
  pageRank_protocol_msgs = gen_protocol_msgs( 8 , result, runs ) # len(data), result )
  pageRank_reqs          = pageRank_protocol_msgs[::2]
  pageRank_resps         = pageRank_protocol_msgs[1::2]

  th = TestHarness( pageRank, pageRank_reqs, pageRank_resps, 
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  th.mem.write_mem( 0x1000, G_data_bytes )
  th.mem.write_mem( 0x2000, R_data_bytes )

  run_sim( th, dump_vcd, max_cycles=MAX_CYCLES )

  if ( runs == 1 ) :
    # Retrieve result from test memory
    result_bytes = struct.pack("<{}L".format(len(result_8data_1run)),*result_8data_1run )
    result_bytes = th.mem.read_mem( 0x2000, len(result_bytes) )
    result_list  = list(struct.unpack("<{}L".format(len(result_8data_1run)), buffer(result_bytes)))
  
    if len(result_list) != len(result_8data_1run):
      print("FAIL, actual result has size " + str(len(result_list)) + " but should have " + str(len(result_8data_1run)))
      return
  
    noError = True
    for i in xrange(len(result_list)):
      if result_list[i] != result_8data_1run[i]:
        print("FAIL, actual result " + str(result_list[i]) + " but should have " + str(result_8data_1run[i]))
        noError = False
  
    if noError:
      print("PASS, Yay!")

  else :
    # Retrieve result from test memory
    result_bytes = struct.pack("<{}L".format(len(result_8data_4run)),*result_8data_4run )
    result_bytes = th.mem.read_mem( 0x2000, len(result_bytes) )
    result_list  = list(struct.unpack("<{}L".format(len(result_8data_4run)), buffer(result_bytes)))
  
    if len(result_list) != len(result_8data_4run):
      print("FAIL, actual result has size " + str(len(result_list)) + " but should have " + str(len(result_8data_4run)))
      return
  
    noError = True
    for i in xrange(len(result_list)):
      if result_list[i] != result_8data_4run[i]:
        print("FAIL, actual result " + str(result_list[i]) + " but should have " + str(result_8data_4run[i]))
        noError = False
  
    if noError:
      print("PASS, Yay!")

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( SchedulerVRTL_alt(), test_params, dump_vcd, test_verilog=False )
