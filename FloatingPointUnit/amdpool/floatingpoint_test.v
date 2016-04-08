module floatingpoint_tb();
    
reg clk, rst, input_a_stb, input_b_stb, output_z_ack;
reg[31:0] input_a, input_b;
wire input_a_ack, input_b_ack, output_z_stb;
wire[31:0] output_z;

multiplier floatingpoint(
        input_a,
        input_b,
        input_a_stb,
        input_b_stb,
        output_z_ack,
        clk,
        rst,
        output_z,
        output_z_stb,
        input_a_ack,
        input_b_ack
);

initial begin
  $monitor("%g a = %h b = %h z = %h", $time, input_a, input_b, output_z);
end

always #5 clk = ~clk;
initial begin
  #0 rst     = 1'b1;
     clk     = 1'b0;
     input_a = 32'b0;
     input_b = 32'b0;
     input_a_stb = 1'b1;
     input_b_stb = 1'b1;
     output_z_ack = 1'b1;  
  #15
     input_a = 32'b00111111110111101011100001010010;
     input_b = 32'b11000001000011000001100010010011;
  #100 
     if (output_z == 32'b11000000111000001000001100010010)
        $display ( "Pass" );
     else
        $display ( "Fail" );
     $finish;
end

initial begin
     $shm_open ("floatingpoint_tb.db");
     $shm_probe(floatingpoint,"AS");
     $dumpfile ("floatingpoint_tb.vcd");
end
endmodule
