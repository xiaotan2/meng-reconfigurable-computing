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




