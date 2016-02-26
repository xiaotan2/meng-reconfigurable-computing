//======================================================================
// SchedulerVRTL
//======================================================================

`include "mem-msgs.v"

module SchedulerVRTL
#(
  parameter nbits  = 32,
  parameter nports = 2
)
(
  input  logic             clk,
  input  logic             reset,

  /* Interface with TestSource and TestSink */

  input  logic             in_req_val,
  input  logic             in_resp_rdy,
  input  logic             in_type,
  input  logic [31:0]      in_addr,
  input  logic [nbits-1:0] in_data,

  output logic             out_req_rdy,
  output logic             out_resp_val,
  output logic             out_type,
  output logic [nbits-1:0] out_data,

  /* Interface with Test Memory */
  
  // memory request port 0 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0] mem_req0_msg,
  output logic                                      mem_req0_val,
  input  logic                                      mem_req0_rdy,

  // memory response port 0 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]   mem_resp0_msg,
  input  logic                                      mem_resp0_val,
  output logic                                      mem_resp0_rdy,
  
  // memory request port 1 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0] mem_req1_msg,
  output logic                                      mem_req1_val,
  input  logic                                      mem_req1_rdy,

  // memory response port 1 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]   mem_resp1_msg,
  input  logic                                      mem_resp1_val,
  output logic                                      mem_resp1_rdy
);

  logic                                             mem_req_val    [0:nports-1];
  logic                                             mem_req_rdy    [0:nports-1];
  logic [2:0]                                       mem_req_type   [0:nports-1];
  logic [31:0]                                      mem_req_addr   [0:nports-1];
  logic [nbits-1:0]                                 mem_req_data   [0:nports-1];
  logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]        mem_req_msg    [0:nports-1];

  logic                                             mem_resp_val   [0:nports-1];  
  logic                                             mem_resp_rdy   [0:nports-1];
  logic [2:0]                                       mem_resp_type  [0:nports-1];
  logic [nbits-1:0]                                 mem_resp_data  [0:nports-1];
  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]          mem_resp_msg   [0:nports-1];

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
  // Pack Memory Request Messages
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

  //----------------------------------------------------------------------- 
  // Two set of registers to store R
  //----------------------------------------------------------------------- 

  // registers
  logic [nbits-1:0] reg_r0 [0:7];
  logic [nbits-1:0] reg_r1 [0:7];
 
  // wires 
  logic [nbits-1:0] reg_r0_d [0:7];
  logic [nbits-1:0] reg_r0_d [0:7];

  integer i;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      reg_r0 <= `{default: 32'b0};
      reg_r1 <= `{default: 32'b0};
    else begin
      for ( i = 0; i < 8; i = i + 1 ) begin
        reg_r0[i] <= reg_r0_d[i];
        reg_r1[i] <= reg_r1_d[i];
      end
    end
  end

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE   = 3'd0;
  localparam STATE_SOURCE = 3'd1;
  localparam STATE_INIT   = 3'd2;
  localparam STATE_START  = 3'd3;
  localparam STATE_RUN    = 3'd4;
  localparam STATE_WAIT   = 3'd5;
  localparam STATE_END    = 3'd6;
  localparam STATE_WRITE  = 3'd7;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [1:0] state_reg;
  logic [1:0] state_next;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
    end
    else begin
      state_reg <= state_next;
    end
  end

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  logic req_go;
  logic resp_go;
  logic start;

  assign req_go       = in_req_val  && out_req_rdy;
  assign resp_go      = out_resp_val && in_resp_rdy;
  assign start        = 1'b1;

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE:   if ( req_go    )    state_next = STATE_SOURCE;
      STATE_SOURCE: if ( start     )    state_next = STATE_INIT;
      STATE_INIT:   if ( resp_go   )    state_next = STATE_START;
      STATE_START:  if ( resp_go   )    state_next = STATE_RUN;
      STATE_RUN:    if ( resp_go   )    state_next = STATE_WAIT;
      STATE_WAIT:   if ( resp_go   )    state_next = STATE_END;  
                    else                state_next = STATE_RUN;
      STATE_END:    if ( resp_go   )    state_next = STATE_WRITE;
      STATE_WRITE:  if ( resp_go   )    state_next = STATE_IDLE;
      default:    state_next = 'x;

    endcase

  end

logic EN_base_G;
assign EN_base_G = 1'b0;
logic EN_base_R;
assign EN_base_R = 1'b0;
logic EN_size;
assign EN_size = 1'b0;


always_ff @ (posedge clk) begin
  if (EN_base_G)
    Base_G <= 
reg base_G;
reg base_R;
reg counter_R;
reg counter_G;
reg counter_global;


always_comb begin
    // IDLE STATE

    // SOURCE STATE
    if(state_reg == STATE_SOURCE) begin
        if(in_req_val == 1'b1 && out_req_rdy == 1'b1) begin
            // Write tpye
            if(in_type == 1'b1) begin
                if(in_addr == 32'b0) begin
                    start = 1'b1;
                end
                else if(in_addr == 32'b1) begin
                    EN_base_G = 1'b1;
                end
                else if(in_addr == 32'd2) begin
                    EN_base_R = 1'b1;
                end
                else if(in_addr == 32'd3) begin
                    EN_size = 1'b1;
                end
                out_type = 1'b1;
                out_data = 32'b0;
                out_resp_val = 1'b1;
            end
            // Read type
            if(in_type == 1'b0) begin
            end
        end
    end

    // INIT STATE
    if(state_reg == STATE_SOURCE) begin
        if(mem_req_rdy[0] == 1'b1 && mem_req_rdy[1] == 1'b1) begin
            mem_req_val[0] = 0'b1;
            mem_req_val[1] = 0'b1;
            mem_req_addr[0] = base_R + 8*counter_R;
            mem_req_addr[1] = base_R + 8*(counter_R)+4;
            mem_req_type[0] = 0'b0;  // Read
            mem_req_type[1] = 0'b0;
        end
    end

    // START STATE
    if(state_reg == STATE_START) begin
        if(mem_req_rdy[0] == 1'b1 && mem_req_rdy[1]) begin
            mem_req_val[0] = 0'b1;
            mem_req_val[1] = 0'b1;
            mem_req_addr[0] = base_G + 8*counter_G;
            mem_req_addr[1] = base_G + 8*(counter_G)+4;
            mem_req_type[0] = 0'b0;  // Read
            mem_req_type[1] = 0'b0;
        end
    end

end
