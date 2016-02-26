//======================================================================
// SchedulerVRTL
//======================================================================

`include "mem-msgs.v"
`include "pageRank-msgs.v"

module pageRankVRTL
#(
  parameter nbits  = 32,
  parameter nports = 2
)
(
  input  logic             clk,
  input  logic             reset,

  /* Interface with TestSource and TestSink */
  input  logic [`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0]   in_req_msg,
  input  logic                                          in_req_val,
  output logic                                          in_req_rdy,

  output logic [`PAGERANK_RESP_MSG_NBITS(1,32)-1:0]     out_resp_msg,
  output logic                                          out_resp_val,
  input  logic                                          out_resp_rdy,

  /* Interface with Test Memory */
  
  // memory request port 0 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]     mem_req0_msg,
  output logic                                          mem_req0_val,
  input  logic                                          mem_req0_rdy,

  // memory response port 0 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]       mem_resp0_msg,
  input  logic                                          mem_resp0_val,
  output logic                                          mem_resp0_rdy,
  
  // memory request port 1 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]     mem_req1_msg,
  output logic                                          mem_req1_val,
  input  logic                                          mem_req1_rdy,

  // memory response port 1 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]       mem_resp1_msg,
  input  logic                                          mem_resp1_val,
  output logic                                          mem_resp1_rdy
);

  // pagerankmsg req

  logic                                                 in_type;
  logic [31:0]                                          in_addr;
  logic [nbits-1:0]                                     in_data;
 
  // pagerankmsg resp

  logic                                                 out_type;
  logic [nbits-1:0]                                     out_data;

  // memory req resp

  logic                                                 mem_req_val    [0:nports-1];
  logic                                                 mem_req_rdy    [0:nports-1];
  logic [2:0]                                           mem_req_type   [0:nports-1];
  logic [31:0]                                          mem_req_addr   [0:nports-1];
  logic [nbits-1:0]                                     mem_req_data   [0:nports-1];
  logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]            mem_req_msg    [0:nports-1];

  logic                                                 mem_resp_val   [0:nports-1];  
  logic                                                 mem_resp_rdy   [0:nports-1];
  logic [2:0]                                           mem_resp_type  [0:nports-1];
  logic [nbits-1:0]                                     mem_resp_data  [0:nports-1];
  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]              mem_resp_msg   [0:nports-1];

  assign mem_req_msg[0]  = mem_req0_msg;
  assign mem_req_msg[1]  = mem_req1_msg;

  assign mem_resp_msg[0] = mem_resp0_msg;
  assign mem_resp_msg[1] = mem_resp1_msg;

  //------------------------------------------------------------------------
  // Pack Memory Request Messages
  //------------------------------------------------------------------------

  vc_MemReqMsgPack#(8, 32, 32) mem_req_msg_pack0
  (
    .type_  (mem_req_type[0]),
    .opaque (8'b0),
    .addr   (mem_req_addr[0]),
    .len    (2'd0),
    .data   (mem_req_data[0]),
    .msg    (mem_req_msg[0])
  );

  vc_MemReqMsgPack#(8, 32, 32) mem_req_msg_pack1
  (
    .type_  (mem_req_type[1]),
    .opaque (8'b0),
    .addr   (mem_req_addr[1]),
    .len    (2'd0),
    .data   (mem_req_data[1]),
    .msg    (mem_req_msg[1])
  );

  //------------------------------------------------------------------------
  // Unpack Memory Response Messages
  //------------------------------------------------------------------------
  
  vc_MemRespMsgUnpack#(8,32) mem_resp_msg_unpack0
  (
    .msg    (mem_resp_msg[0]),
    .opaque (),
    .type_  (mem_resp_type[0]),
    .test   (),
    .len    (),
    .data   (mem_resp_data[0])
  );

  vc_MemRespMsgUnpack#(8,32) mem_resp_msg_unpack1
  (
    .msg    (mem_resp_msg[1]),
    .opaque (),
    .type_  (mem_resp_type[1]),
    .test   (),
    .len    (),
    .data   (mem_resp_data[1])
  );

  //-------------------------------------------------------------------------
  // Pack pageRank Request Messages
  //-------------------------------------------------------------------------

  pageRankReqMsgUnpack#(1,32,32) pageRankReq_Msg_Unpack
  (
    .msg    (in_req_msg),
    .type_  (in_type),
    .addr   (in_addr),
    .data   (in_data)
  );

  pageRankRespMsgPack#(1,32) pageRankResp_Msg_Pack
  (
    .msg    (out_resp_msg),
    .type_  (out_type),
    .data   (out_data)
  );

  //----------------------------------------------------------------------- 
  // Connection Wires
  //----------------------------------------------------------------------- 

  // declared wires for Scheduler


  // declared wires for Mapper

  
  // declared wires for Reducer


  //----------------------------------------------------------------------- 
  // Scheduler
  //----------------------------------------------------------------------- 

  SchedulerVRTL sche
  (
    .clk,     (clk),
    .reset,   (reset)

  /* Interface with TestSource and TestSink */
  input  logic [`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0]   in_req_msg[`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0] ,
  input  logic                                          in_req_val,
  output logic                                          in_req_rdy,

  output logic [`PAGERANK_RESP_MSG_NBITS(1,32)-1:0]     out_resp_msg[`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0] ,
  output logic                                          out_resp_val,
  input  logic                                          out_resp_rdy,

  /* Interface with Test Memory */
  
  // memory request port 0 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]     mem_req0_msg,[`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0] 
  output logic                                          mem_req0_val,
  input  logic                                          mem_req0_rdy,

  // memory response port 0 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]       mem_resp0_msg,[`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0] 
  input  logic                                          mem_resp0_val,
  output logic                                          mem_resp0_rdy,
  
  // memory request port 1 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]     mem_req1_msg,[`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0] 
  output logic                                          mem_req1_val,
  input  logic                                          mem_req1_rdy,

  // memory response port 1 
  .(mem_resp1_msg)                                      (mem_resp1_msg[`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]),
  .(mem_resp1_val)                                      (mem_resp1_val),
  .(mem_resp1_rdy)                                      (mem_resp1_rdy)
  );

  //----------------------------------------------------------------------
  // Mappers
  //----------------------------------------------------------------------

  MapperVRTL mapper0
  (
  );

  //----------------------------------------------------------------------
  // Reducers
  //----------------------------------------------------------------------

  ReducerVRTL reducer0
  (
  );

endmodule
