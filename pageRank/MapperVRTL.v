//======================================================================
// MapperVRTL
//======================================================================

module MapperVRTL
#(
  parameter nbits = 32
)
(
  input  clk;
  input  reset;
  input  [nbits-1:0] r_0,
  input  [nbits-1:0] r_1,
  input  [nbits-1:0] g_0,
  input  [nbits-1:0] g_1,
  output [nbits-1:0] out
);

logic [nbits-1:0] prod0;
logic [nbits-1:0] prod1;

assign prod0 = r_0*g_0;
assign prod1 = r_0*g_0;
assign out   = prod0 + prod1;

always

endmodule
