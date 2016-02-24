//======================================================================
// SchedulerVRTL
//======================================================================

module SchedulerVRTL
#(
  parameter nbits = 32
)
(
  input  [nbits-1:0] ,
  input  [nbits-1:0] r_1,
  input  [nbits-1:0] g_0,
  input  [nbits-1:0] g_1,
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

endmodule
