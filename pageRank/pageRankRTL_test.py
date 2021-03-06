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

from pageRankRTL     import pageRankRTL
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
MAX_CYCLES  = 200000

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness (Model):

  def __init__( s, pageRankRTL, src_msgs, sink_msgs,
               stall_prob, latency, src_delay, sink_delay,
               dump_vcd=False, test_verilog=False ):

    # Instantiate Models
    s.src       = TestSource    ( pageRankReqMsg(),  src_msgs,  src_delay  )
    s.di        = pageRankRTL
    s.sink      = TestSink      ( pageRankRespMsg(), sink_msgs, sink_delay )
    s.mem       = TestMemory    ( MemMsg(8,32,64), 2, stall_prob, latency   )

    # Dump VCD
    if dump_vcd:
      s.di.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.di = TranslationTool( s.di )

    # Connect
    s.connect( s.src.out,           s.di.direq        )
    s.connect( s.di.diresp,         s.sink.in_        )
    s.connect( s.di.memreq,         s.mem.reqs[0]     )
    s.connect( s.di.memresp,        s.mem.resps[0]    )

  def done(s):
    return s.src.done and s.sink.done
  
  def line_trace(s):
    return s.di.line_trace(mapper_num = MAPPER_NUM, reducer_num = REDUCER_NUM)
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

def gen_protocol_msgs( G_size, R_size, result ):
  return [
    req( 'wr', 1, 0x1000 ), resp( 'wr', 0      ),
    req( 'wr', 2, 0x2000 ), resp( 'wr', 0      ),
    req( 'wr', 3, 0x3000 ), resp( 'wr', 0      ),
    req( 'wr', 4, G_size ), resp( 'wr', 0      ),
    req( 'wr', 5, R_size ), resp( 'wr', 0      ),
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

# vector R
vectorR = []

# test data 8x8 matrix
test_8data = []
result_8data = []
for i in xrange(8):
  for j in xrange(8):
    test_8data.append(i)

for i in xrange(8):
  vectorR.append(i)

result_8data = dot(vectorR, vectorToMatrix(test_8data, 8))

# transpose test_8data, and combine 4 of them into 1
matrix_test = vectorToMatrix(test_8data, 8)
matrix_test = transpose(matrix_test)
test_8data = matrixToVector(matrix_test, 8)

test_8data = fourElementsToOne(test_8data)
result_8data = fourElementsToOne(result_8data)
vectorR = fourElementsToOne(vectorR)

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------
test_case_table = mk_test_case_table([
  (                  "G_data       R_data         result       stall  latency  src_delay  sink_delay" ),
  [ "test8_0x0x0",   test_8data,   vectorR,         1,           0,     0,       0,         0         ],
])

#-------------------------------------------------------------------------
# Run Test
#-------------------------------------------------------------------------

def run_test( pageRank, test_params, dump_vcd, test_verilog=False ):

  G_data       = test_params.G_data
  R_data       = test_params.R_data
  result       = test_params.result
  G_data_bytes = struct.pack("<{}L".format(len(G_data)), *G_data)
  R_data_bytes = struct.pack("<{}L".format(len(R_data)), *R_data)
  
  pageRank_protocol_msgs = gen_protocol_msgs( len(G_data), len(R_data), result )
  pageRank_reqs          = pageRank_protocol_msgs[::2]
  pageRank_resps         = pageRank_protocol_msgs[1::2]

  th = TestHarness( pageRank, pageRank_reqs, pageRank_resps, 
                    test_params.stall, test_params.latency,
                    test_params.src_delay, test_params.sink_delay,
                    dump_vcd, test_verilog )

  th.mem.write_mem( 0x1000, G_data_bytes )
  th.mem.write_mem( 0x2000, R_data_bytes )
  run_sim( th, dump_vcd, max_cycles=MAX_CYCLES )

  # Retrieve result from test memory
  result_bytes = struct.pack("<{}L".format(len(test_8data)),*result_8data )
  result_bytes = th.mem.read_mem( 0x3000, len(result_bytes) )
  result_list  = list(struct.unpack("<{}L".format(len(result_8data)), buffer(result_bytes)))

  if len(result_list) != len(result_8data):
    print("FAIL, actual result has size " + str(len(result_list)) + " but should have " + str(len(result_8data)))
    return

  noError = True
  for i in xrange(len(result_list)):
    if result_list[i] != result_8data[i]:
      print("FAIL, actual result " + str(result_list[i]) + " but should have " + str(result_8data[i]))
      noError = False

  if noError:
    print("PASS, Yay!")

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_test( pageRankRTL(mapper_num = MAPPER_NUM, reducer_num = REDUCER_NUM, train_size = TRAIN_SIZE, k = k), test_params, dump_vcd, test_verilog=False )
