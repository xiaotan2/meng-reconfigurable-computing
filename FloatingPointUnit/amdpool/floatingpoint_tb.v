module floatingpoint_tb();
    
reg clk, rst, input_a_stb, input_b_stb, output_z_ack;
reg[31:0] input_a, input_b;
wire input_a_ack, input_b_ack, output_z_stb;
wire[31:0] output_z;
wire[3:0] state;

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
  $monitor("%g a(%b|%b) b(%b|%b) a = %h b = %h z = %h z(%b|%b)", 
        $time, input_a_stb, input_a_ack, input_b_stb, input_b_ack, input_a, input_b, output_z, output_z_stb, output_z_ack );
end

always #5 clk = ~clk;
initial begin
  #0 rst     = 1'b1;
     clk     = 1'b0;
  #10 
     rst = 1'b0; 
     input_a_stb = 1'b1;
     input_b_stb = 1'b1;
 
     input_a = 32'b00111111110111101011100001010010; // 1.74
     input_b = 32'b11000001000011000001100010010011; // -8.756

     output_z_ack = 1'b1;

  #180 
     if (output_z == 32'b11000001011100111100010001011100) // 15.23544
        $display ( "Pass" );
     else
        $display ( "Fail" );
     $stop;
end

//initial begin
//     $shm_open ("floatingpoint_tb.db");
//     $shm_probe(floatingpoint,"AS");
//     $dumpfile ("floatingpoint_tb.vcd");
//end
endmodule
