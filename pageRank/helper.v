//======================================================================
// Helper modules
//======================================================================

//----------------------------------------------------------------------
// Registers
//----------------------------------------------------------------------

module regEN 
#(
  parameter nbits = 32
)
(
  input clk,
  input reset,

  input  [nbits-1:0] reg_d,
  input              reg_en,
  output [nbits-1:0] reg_q
);

  always_ff @ (posedge clk) begin
    if ( reset )  
      reg_q <= 0;
    else if ( reg_en )
      reg_q <= reg_d;
    else
      reg_q <= reg_q;    
  end

endmodule


//----------------------------------------------------------------------
// Counters
//----------------------------------------------------------------------

module counter 
#(
  parameter nbits     = 32,
  parameter increment = 1
)
(
  input clk,
  input reset,

  input              count_clear,
  input              count_en,
  output [nbits-1:0] count_out
);

  always_ff @ (posedge clk) begin
    if ( reset || count_clear)  
      count_out <= 0;
    else if ( count_en )
      count_out <= count_out + increment ;
    else
      count_out <= count_out;    
  end

endmodule

module counterSET 
#(
  parameter nbits     = 32,
  parameter increment = 1
)
(
  input clk,
  input reset,

  input              count_clear,
  input              count_set,
  input              count_en,
  output [nbits-1:0] count_out
);

  always_ff @ (posedge clk) begin
    if ( reset || count_clear)  
      count_out <= 0;
    else if ( count_set )
      count_out <= 1;
    else if ( count_en )
      count_out <= count_out + increment ;
    else
      count_out <= count_out;    
  end

endmodule

//----------------------------------------------------------------------
// Muxes
//----------------------------------------------------------------------

module mux2 
#(
  parameter nbits     = 32
)
(
  input              sel,
  input  [nbits-1:0] in_0,
  input  [nbits-1:0] in_1,
  output [nbits-1:0] out
);

  assign out = (sel == 1'b0) ? in_0 : in_1;

endmodule



module mux8 
#(
  parameter nbits     = 32
)
(
  input  [      2:0]  sel,
  input  [nbits-1:0] in_0,
  input  [nbits-1:0] in_1,
  input  [nbits-1:0] in_2,
  input  [nbits-1:0] in_3,
  input  [nbits-1:0] in_4,
  input  [nbits-1:0] in_5,
  input  [nbits-1:0] in_6,
  input  [nbits-1:0] in_7,
  output [nbits-1:0] out
);

  always_comb begin
    case( sel )
      3'd0: out = in_0;
      3'd1: out = in_1;
      3'd2: out = in_2;
      3'd3: out = in_3;
      3'd4: out = in_4;
      3'd5: out = in_5;
      3'd6: out = in_6;
      3'd7: out = in_7;
    endcase   
  end

endmodule


module mux4_2sel
#(
  parameter nbits     = 32
)
(
  input             sel_0,
  input             sel_1,
  input  [nbits-1:0] in_0,
  input  [nbits-1:0] in_1,
  input  [nbits-1:0] in_2,
  input  [nbits-1:0] in_3,
  output [nbits-1:0] out
);

  logic [nbits-1:0] mux0_out;
  logic [nbits-1:0] mux1_out;

  assign mux0_out = (sel_0 == 1'b0) ? in_0     : in_1;
  assign mux1_out = (sel_0 == 1'b0) ? in_2     : in_3;
  assign out      = (sel_1 == 1'b0) ? mux0_out : mux1_out;

endmodule



