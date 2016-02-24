//======================================================================
// ReducerVRTL
//======================================================================

// 4-input adder tree

module ReducerVRTL
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

assign out   = in0 + in1 + in2 + in3;

endmodule
