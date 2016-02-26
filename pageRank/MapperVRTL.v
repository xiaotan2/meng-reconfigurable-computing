//======================================================================
// MapperVRTL
//======================================================================

// 2 multiplier 1 adder

module MapperVRTL
#(
  parameter nbits = 32
)
(
  input  clk,
  input  reset,

  input  [nbits-1:0] r_0,
  input  [nbits-1:0] g_0,
  input  [nbits-1:0] r_1,
  input  [nbits-1:0] g_1,

  output [nbits-1:0] out
);

// register wires

logic [nbits-1:0] prod0_d;
logic [nbits-1:0] prod1_d;
logic [nbits-1:0] prod0_q;
logic [nbits-1:0] prod1_q;

// multiply r entry by g entry

assign prod0_d = r_0 * g_0;
assign prod1_d = r_1 * g_1;

// two nbits registers

always_ff @( posedge clk ) begin
  if ( reset ) begin
    prod0_q <= 0;
    prod1_q <= 0;
  end
  else begin
    prod0_q <= prod0_d;
    prod1_q <= prod1_d;
  end
end

// add products together

assign out   = prod0_q + prod1_q;


endmodule
