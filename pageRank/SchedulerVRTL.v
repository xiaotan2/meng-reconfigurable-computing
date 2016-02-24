//======================================================================
// SchedulerVRTL
//======================================================================

module SchedulerVRTL
#(
  parameter nbits = 32
)
(
  // input signals from test source

  input              in_req_val,
  input              in_resp_rdy,
  input              in_type,
  input              in_addr,
  input              in_data,

  // output signals to test sink

  output             out_req_rdy,
  output             out_resp_val,

  input  [nbits-1:0] reg_r1_in0,
  input  [nbits-1:0] reg_r1_in1,
  input  [nbits-1:0] reg_r1_in2,
  input  [nbits-1:0] reg_r1_in3,
  input  [nbits-1:0] reg_r1_in4,
  input  [nbits-1:0] reg_r1_in5,
  input  [nbits-1:0] reg_r1_in6,
  input  [nbits-1:0] reg_r1_in7,
  
  output [nbits-1:0] out
);


logic [nbits-1:0] reg_r1 [0:7];
logic [nbits-1:0] reg_r2 [0:7];

always @( posedge clk, posedge reset ) begin
  if ( reset ) begin
    reg_r0 <= 32'b0;
    reg_r1 <= 32'b0;
  else
end

//----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE   = 2'd0;
  localparam STATE_SOURCE = 2'd1;
  localparam STATE_INIT   = 2'd2;

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

  assign req_go       = in_req_val  && in_req_rdy;
  assign resp_go      = out_resp_val && out_resp_rdy;
  assign start        = 0;

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE:   if ( req_go    )    state_next = STATE_SOURCE;
      STATE_SOURCE: if ( start     )    state_next = STATE_INIT;
      STATE_INIT:   if ( resp_go   )    state_next = STATE_IDLE;
      default:    state_next = 'x;

    endcase

  end

  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------

  localparam b_a   = 1'd1;

  task cs
  (
    input logic       cs_out_req_rdy,
    input logic       cs_out_resp_val,
  );
  begin
    out_req_rdy    = cs_out_req_rdy;
    out_resp_val   = cs_out_resp_val;
  end
  endtask

  // Set outputs using a control signal "table"

  always_comb begin

    cs( 0, 0 );
    case ( state_reg )
      //                             req resp 
      //                             rdy val  
      STATE_IDLE:                cs( 1,  0,   );
      STATE_SOURCE:              cs( 0,  0,   );
      STATE_INIT:                cs( 0,  1,   );
      default                    cs('x, 'x,   );

    endcase

  end


endmodule
