//======================================================================
// MapperVRTL
//======================================================================

module MapperVRTL
#(
  parameter nbits = 32
)
(
  input  [nbits-1:0] in0,
  input  [nbits-1:0] in1,
  input  [nbits-1:0] in2,
  input  [nbits-1:0] in3,
  output [nbits-1:0] out
);

logic [nbits-1:0] prod0;
logic [nbits-1:0] prod1;

assign prod0 = in0*in1;
assign prod1 = in2*in3;
assign out   = prod0 + prod1;

endmodule
