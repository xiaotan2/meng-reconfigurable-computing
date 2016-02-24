//======================================================================
// SchedulerVRTL
//======================================================================

module SchedulerVRTL
#(
  parameter nbits  = 32
  parameter nports = 2
)
(
  /* Interface with TestSource and TestSink */

  input              in_req_val,
  input              in_resp_rdy,
  input              in_type,
  input [31:0]       in_addr,
  input [31:0]       in_data,

  output             out_req_rdy,
  output             out_resp_val,
  output             out_type,
  output             out_addr,
  output [31:0]      out_data,

  /* Interface with Test Memory */

  input              mem_resp_val   [0:nports-1],
  input              mem_req_rdy    [0:nports-1],
  input              mem_resp_type  [0:nports-1], 
  input [31:0]       mem_resp_addr  [0:nports-1],
  input [nbits-1:0]  mem_resp_data  [0:nports-1],

  output             mem_req_val    [0:nports-1],
  output             mem_resp_rdy   [0:nports-1],
  output             mem_req_type   [0:nports-1],
  output [31:0]      mem_req_addr   [0:nports-1],
  output [nbits-1:0] mem_req_data   [0:nports-1]
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
  assign start        = 0;

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE:   if ( req_go    )    state_next = STATE_SOURCE;
      STATE_SOURCE: if ( start     )    state_next = STATE_INIT;
      STATE_INIT:   if ( resp_go   )    state_next = STATE_START;
      STATE_START:  if ( resp_go   )    state_next = STATE_RUN;
      STATE_RUN:    if ( resp_go   )    state_next = STATE_WAIT;
      STATE_WAIT:   if ( resp_go   )    state_next = STATE_END;   else if () state_next = STATE_RUN;
      STATE_END:    if ( resp_go   )    state_next = STATE_WRITE;
      STATE_WRITE:  if ( resp_go   )    state_next = STATE_IDLE;
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
      STATE_START:               cs( 0,  1,   );
      STATE_RUN:                 cs( 0,  1,   );
      STATE_WAIT:                cs( 0,  1,   );
      STATE_END:                 cs( 0,  1,   );
      STATE_WRITE:               cs( 0,  1,   );
      default                    cs('x, 'x,   );

    endcase

  end


endmodule
