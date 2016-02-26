//======================================================================
// pageRankVRTL
//======================================================================

`include "mem-msgs.v"
`include "pageRank-msgs.v"

module pageRankVRTL
#(
  parameter nbits  = 32,
  parameter nports = 2,
  parameter n      = 8,
  parameter num_mappers = 4,
  parameter num_reducers = 1  
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


  //----------------------------------------------------------------------- 
  // Connection Wires
  //----------------------------------------------------------------------- 

   logic [num_mappers*2-1:0] mapper_r;
   logic [num_mappers*2-1:0] mapper_g;
   logic [n-1:0]             result;
   logic [num_mapers-1:0   ] out;

  //----------------------------------------------------------------------- 
  // Scheduler
  //----------------------------------------------------------------------- 

  SchedulerVRTL scheduler
#(
  parameter nbits  = 32,
  parameter nports = 2,
  parameter n      = 8,
  parameter num_mappers = 4,
  parameter num_reducers = 1
)
  (
    .clk,     (clk),
    .reset,   (reset),

  /* Interface with TestSource and TestSink */
    .in_req_msg        (in_req_msg),
    .in_req_val        (in_req_val),
    .in_req_rdy        (in_req_rdy),
                                     
    .out_resp_msg      (out_resp_msg),
    .out_resp_val      (out_resp_val),
    .out_resp_rdy      (out_resp_rdy),

  /* Interface with Test Memory */
  
  // memory request port 0 
    .mem_req0_msg     (mem_req0_msg),
    .mem_req0_val     (mem_req0_val),
    .mem_req0_rdy     (mem_req0_rdy),

  // memory response port 0 
    .mem_resp0_msg    (mem_resp0_msg),
    .mem_resp0_val    (mem_resp0_val),
    .mem_resp0_rdy    (mem_resp0_rdy),
  
  // memory request port 1 
    .mem_req1_msg     (mem_req1_msg),
    .mem_req1_val     (mem_req1_val),
    .mem_req1_rdy     (mem_req1_rdy),
 
  // memory response port 1 
    .mem_resp1_msg    (mem_resp1_msg),
    .mem_resp1_val    (mem_resp1_val),
    .mem_resp1_rdy    (mem_resp1_rdy),

  /* Interface with Mappers */
    .mapper_r         (mapper_r),
    .mapper_g         (mapper_g),

  /* Interface with Reducers */
    .reducer_result   (result)

  );


  //----------------------------------------------------------------------
  // Mappers
  //----------------------------------------------------------------------

genvar i;
generate
  for (i = 0; i < num_mappers; i = i + 1) begin: MAPPER
     MapperVRTL mapper
     #(
       parameter nbits = 32
     )
     (
       .clk     (clk),
       .reset   (reset),
     
       .r_0     (mapper_r[0+i*2]),
       .g_0     (mapper_g[0+i*2]),
       .r_1     (mapper_r[1+i*2]),
       .g_1     (mapper_g[1+i*2]),
     
       .out     (out[i])
     );
  
  end
endgenerate


  //----------------------------------------------------------------------
  // Reducers
  //----------------------------------------------------------------------
generate
  for (i = 0; i < num_reducers; i = i + 1) begin: REDUCER
     ReducerVRTL reducer
     #(
       parameter nbits = 32
     )
     (
       .in0     (out[0+4*i]),    
       .in1     (out[1+4*i]),
       .in2     (out[2+4*i]),
       .in3     (out[3+4*i]),
       .out     (result[i])
     );
   end
endgenerate

endmodule
