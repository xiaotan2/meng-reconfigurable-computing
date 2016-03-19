//======================================================================
// SchedulerVRTL
//======================================================================

`include "mem-msgs.v"
`include "pageRank-msgs.v"
`include "helper.v"

`include "trace.v"


module SchedulerVRTL
#(
  parameter nbits  = 8,
  parameter nports = 1,
  parameter bw     = 32,
  parameter n      = 8
)
(
  input  logic             clk,
  input  logic             reset,

  /* Interface with TestSource and TestSink */
  input  logic [`PAGERANK_REQ_MSG_NBITS(1,32,32)-1:0]   pr_req_msg,
  input  logic                                          pr_req_val,
  output logic                                          pr_req_rdy,

  output logic [`PAGERANK_RESP_MSG_NBITS(1,32)-1:0]     pr_resp_msg,
  output logic                                          pr_resp_val,
  input  logic                                          pr_resp_rdy,

  /* Interface with Test Memory */
  
  // memory request port 0 
  output logic [`VC_MEM_REQ_MSG_NBITS(8,32,32)-1:0]     mem_req_msg,
  output logic                                          mem_req_val,
  input  logic                                          mem_req_rdy,

  // memory response port 0 
  input  logic [`VC_MEM_RESP_MSG_NBITS(8,32)-1:0]       mem_resp_msg,
  input  logic                                          mem_resp_val,
  output logic                                          mem_resp_rdy
  
);
  // size of G reg array
  localparam m = nports * bw / nbits;

  // max countR, number of times load partial R
  localparam max_R = n * nbits / (bw * nports);

  // pagerankmsg req resp

  logic                                                 pr_req_type;
  logic [31:0]                                          pr_req_addr;
  logic [31:0]                                          pr_req_data;
 
  logic                                                 pr_resp_type;
  logic [31:0]                                          pr_resp_data;

  // memory req resp

  logic [2:0]                                           mem_req_type ;
  logic [31:0]                                          mem_req_addr ;
  logic [31:0]                                          mem_req_data ;

  logic [2:0]                                           mem_resp_type;
  logic [31:0]                                          mem_resp_data;


  //------------------------------------------------------------------------
  // Pack Memory Request Messages
  //------------------------------------------------------------------------

  vc_MemReqMsgPack#(8, 32, 32) mem_req_msg_pack
  (
    .type_  (mem_req_type),
    .opaque (8'b0),
    .addr   (mem_req_addr),
    .len    (2'd0),
    .data   (mem_req_data),
    .msg    (mem_req_msg)
  );


  //------------------------------------------------------------------------
  // Unpack Memory Response Messages
  //------------------------------------------------------------------------
  
  vc_MemRespMsgUnpack#(8,32) mem_resp_msg_unpack
  (
    .msg    (mem_resp_msg),
    .opaque (),
    .type_  (mem_resp_type),
    .test   (),
    .len    (),
    .data   (mem_resp_data)
  );


  //------------------------------------------------------------------------
  // split 32-bit data to 4 8-bit data
  //------------------------------------------------------------------------

  logic [nbits-1:0] data[0:m-1];

  assign data[0] = mem_resp_data[ 7: 0];  
  assign data[1] = mem_resp_data[15: 8];  
  assign data[2] = mem_resp_data[23:16];  
  assign data[3] = mem_resp_data[31:24];  

  //-------------------------------------------------------------------------
  // Pack pageRank Request Messages
  //-------------------------------------------------------------------------

  pageRankReqMsgUnpack#(1,32,32) pageRankReq_Msg_Unpack
  (
    .msg    (pr_req_msg),
    .type_  (pr_req_type),
    .addr   (pr_req_addr),
    .data   (pr_req_data)
  );

  pageRankRespMsgPack#(1,32) pageRankResp_Msg_Pack
  (
    .msg    (pr_resp_msg),
    .type_  (pr_resp_type),
    .data   (pr_resp_data)
  );

  //-------------------------------------------------------------------------
  // regs base address of G and R, size
  //-------------------------------------------------------------------------
  
  logic [31:0]  base_G;
  logic [31:0]  base_R;
  logic [31:0]  size;
  
  logic         base_G_en;
  logic         base_R_en;
  logic         size_en;
 
  regEN #(32) base_G_reg
  (
    .clk    ( clk         ),
    .reset  ( reset       ),
    .reg_d  ( pr_req_data ),
    .reg_q  ( base_G      ),
    .reg_en ( base_G_en   )
  );
   
  regEN #(32) base_R_reg
  (
    .clk    ( clk         ),
    .reset  ( reset       ),
    .reg_d  ( pr_req_data ),
    .reg_q  ( base_R      ),
    .reg_en ( base_R_en   )
  );
   
  
  regEN #(32) size_reg
  (
    .clk    ( clk         ),
    .reset  ( reset       ),
    .reg_d  ( pr_req_data ),
    .reg_q  ( size        ),
    .reg_en ( size_en     )
  );
   

  //----------------------------------------------------------------------- 
  // Two set of registers to store R
  //----------------------------------------------------------------------- 

  // registers
  logic [nbits-1:0] reg_r0 [0:n-1];
  logic [nbits-1:0] reg_r1 [0:n-1];
 
  // wires 
  logic [nbits-1:0] reg_r0_d [0:n-1];
  logic [nbits-1:0] reg_r1_d [0:n-1];

  // wires, wr enable  
  logic             reg_r0_en [0:n-1];
  logic             reg_r1_en [0:n-1];

  integer i;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      for ( i = 0; i < n; i = i + 1 ) begin
        reg_r0[i] <= 8'b0;
        reg_r1[i] <= 8'b0;
      end
    end
    else begin
      for ( i = 0; i < n; i = i + 1 ) begin
        if ( reg_r0_en[i] == 1'b1 ) 
          reg_r0[i] <= reg_r0_d[i];
        else 
          reg_r0[i] <= reg_r0[i];
        if ( reg_r1_en[i] == 1'b1 ) 
          reg_r1[i] <= reg_r1_d[i];
        else 
          reg_r1[i] <= reg_r1[i];
      end
    end
  end

  // r0 reg muxes
  logic mux_r0_sel [0:m-1];
  logic [nbits-1:0] res;

  always_comb begin
    for ( i = 0; i < m; i = i + 1 ) begin
      if ( mux_r0_sel[i] == 1'b0 ) begin
        reg_r0_d[i] = data[i];
      end
      else begin
        reg_r0_d[i] = res;
      end
    end
  end

  //----------------------------------------------------------------------- 
  // Registers to store one column of G
  //----------------------------------------------------------------------- 

  // registers
  logic [nbits-1:0] reg_g [0:m-1];
 
  // wires 
  logic [nbits-1:0] reg_g_d [0:m-1];

  // wires, wr enable  
  logic             reg_g_en [0:m-1];

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      for ( i = 0; i < m; i = i + 1 ) begin
        reg_g[i] <= 8'b0;
      end
    end
    else begin
      for ( i = 0; i < m; i = i + 1 ) begin
        if ( reg_g_en[i] == 1'b1 ) 
          reg_g[i] <= reg_g_d[i];
        else 
          reg_g[i] <= reg_g[i];
      end
    end
  end

  // connect data[i] to reg_g[i]
  always_comb begin
    for ( i = 0; i < m; i = i + 1 ) begin
      reg_g_d[i] = data[i];
    end
  end

  //----------------------------------------------------------------------
  // Calculation unit
  //----------------------------------------------------------------------

  logic [nbits-1:0] wire_r [0:m-1];
  logic [nbits-1:0] sum;

  assign sum = wire_r[0]*reg_g[0] + wire_r[1]*reg_g[1] + wire_r[2]*reg_g[2] + wire_r[3]*reg_g[3];


  always_comb begin
    for ( i = 0; i < m; i = i + 1 )
      wire_r[i] = reg_r0[i];

    for ( i = 0; i < n; i = i + 1 )
      reg_r1_d[i] = res;

  end

  logic [nbits-1:0] r1_rd_mux_out;

  mux8 #(nbits) r1_rd_mux
  ( 
    .in_0         (  reg_r1[0]     ),
    .in_1         (  reg_r1[1]     ),
    .in_2         (  reg_r1[2]     ),
    .in_3         (  reg_r1[3]     ),
    .in_4         (  reg_r1[4]     ),
    .in_5         (  reg_r1[5]     ),
    .in_6         (  reg_r1[6]     ),
    .in_7         (  reg_r1[7]     ),
    .sel          (  count_G[2:0]-3'b1 ),
    .out          (  r1_rd_mux_out )
  );

  assign res = (count_R > 32'b1) ? (sum + r1_rd_mux_out) : sum;

  //----------------------------------------------------------------------
  // Counters
  //
  // counter_R iterate R
  // counter_G iterate G's column
  // counter_W
  // counter_C
  //----------------------------------------------------------------------

  logic        count_R_clear;
  logic        count_R_en;
  logic [31:0] count_R;

  counter #(32, 1) counter_R
  (
    .clk         (clk          ),
    .reset       (reset        ),
    .count_clear (count_R_clear),
    .count_en    (count_R_en   ),
    .count_out   (count_R      )    
  );
 
  logic        count_G_clear;
  logic        count_G_en;
  logic [31:0] count_G;

  counter #(32, 1) counter_G
  (
    .clk         (clk          ),
    .reset       (reset        ),
    .count_clear (count_G_clear),
    .count_en    (count_G_en   ),
    .count_out   (count_G      )    
  ); 


  //----------------------------------------------------------------------- 
  // Address Calculation for R and G
  //----------------------------------------------------------------------- 

  // Address to read/write R

  logic [31:0] addr_R;

  assign addr_R = count_R*(bw/nbits) + base_R; 

  // Address to read/write G

  logic [31:0] addr_G;

  assign addr_G = count_G*n + base_G + (bw/nbits)*(count_R-32'b1);
 
  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------


  typedef enum logic [$clog2(16)-1:0] {
    STATE_INIT  , 
    STATE_READR , 
    STATE_WAITR ,
    STATE_READG , 
    STATE_WAITG ,
    STATE_RUN   , 
    STATE_WAIT  , 
    STATE_END   , 
    STATE_WRITE  
  } state_t;


  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [3:0] state_reg;
  logic [3:0] state_next;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_INIT;
    end
    else begin
      state_reg <= state_next;
    end
  end

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  localparam pr_rd  = 1'b0;
  localparam pr_wr  = 1'b1;
  localparam pr_x   = 1'bx;

  localparam mem_rd = 3'b0;
  localparam mem_wr = 3'b1;
  localparam mem_x  = 3'bx;

  logic pr_req_go;
  logic pr_resp_go;

  logic go;

  logic mem_req_go;
  logic mem_resp_go;

  assign pr_req_go       = pr_req_val  && pr_req_rdy;
  assign pr_resp_go      = pr_resp_val && pr_resp_rdy;

  assign go              = pr_req_go && ( pr_req_type == pr_wr ) && ( pr_req_addr == 32'd0 );

  assign mem_req_go      = mem_req_val  && mem_req_rdy;
  assign mem_resp_go     = mem_resp_val && mem_resp_rdy;


  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_INIT:  if ( go                )              state_next = STATE_READR; 
      STATE_READR: if ( mem_req_go        )              state_next = STATE_WAITR;
      STATE_WAITR: if ( mem_resp_go       )              state_next = STATE_READG;
      STATE_READG: if ( mem_req_go        )              state_next = STATE_WAITG;
      STATE_WAITG: if ( mem_resp_go && count_G == n && count_R == max_R )   state_next = STATE_INIT;
                   else if ( mem_resp_go && count_G == n )                  state_next = STATE_READR;
                   else if ( mem_resp_go  )                                 state_next = STATE_READG;

//      STATE_START:  if ( counter_G == 3'd3  )  state_next = STATE_RUN;
//      STATE_RUN:    if ( red_resp_val  )       state_next = STATE_WAIT;
//      STATE_WAIT:   if ( resp_go   )           state_next = STATE_END;  
//      STATE_END:    if ( resp_go   )           state_next = STATE_WRITE;
//      STATE_WRITE:  if ( resp_go   )           state_next = STATE_SOURCE;
      default:    state_next = 'x;

    endcase

  end

  //logic         mem_request;
  //logic [31:0]  mem_addr_d;
  //logic [31:0]  mem_data_d;
  //logic         mem_type_d;
  //
  //
  //// combination block interacting with memory
  //always_comb begin
  //
  //    // Memory Request
  //    if(mem_request == 1'b1) begin
  //        mem_req_val  = 1'b1;
  //        mem_req_addr = mem_addr_d;
  //        mem_req_type = mem_type_d;
  //        mem_req_data = mem_data_d;
  //    end
  //    else begin
  //        mem_req_val  = 1'b0;
  //        mem_req_addr = 32'b0;
  //        mem_req_type = 1'b0;
  //        mem_req_data = 32'b0;
  //    end
  //
  //    // Memory Response
  //    if(mem_resp_val[0] == 1'b1 && mem_resp_val[1] == 1'b1) begin
  //        mem_resp_rdy[0] = 1'b1;
  //        mem_resp_rdy[1] = 1'b1;
  //    end
  //end
  
  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------
  
  logic load_base_R;
  logic load_base_G;
  logic load_size;
  
  assign load_base_G = pr_req_go && ( pr_req_addr == 32'd1 );
  assign load_base_R = pr_req_go && ( pr_req_addr == 32'd2 );
  assign load_size   = pr_req_go && ( pr_req_addr == 32'd3 );
  
  
  always_comb begin
  
      // default values
  
      pr_req_rdy   = 1'b0;
      pr_resp_val  = 1'b0;
  
      mem_req_val  = 1'b0;
      mem_resp_rdy = 1'b0;
  
      base_G_en    = 1'b0;
      base_R_en    = 1'b0;
      size_en      = 1'b0;
  
      count_R_en    = 1'b0;
      count_R_clear = 1'b0;

      count_G_en    = 1'b0;
      count_G_clear = 1'b0;

      for ( i = 0; i < n; i = i + 1 ) begin
        reg_r0_en[i] = 1'b0;
        reg_r1_en[i] = 1'b0;
      end
      for ( i = 0; i < m; i = i + 1 ) begin
        reg_g_en[i] = 1'b0;
      end
      /////////////////////////  INIT STATE    ///////////////////////////////////
  
      if( state_reg == STATE_INIT ) begin
  
        pr_req_rdy  = pr_resp_rdy;
        pr_resp_val = pr_req_val;
  
        // Write tpye
        if ( pr_req_type == pr_wr ) begin
          if ( go ) begin
            // clear count_R
            count_R_clear = 1'b1; 
          end
          else if( load_base_G ) begin
            base_G_en  = 1'b1;
          end
          else if( load_base_R ) begin
            base_R_en  = 1'b1;
          end
          else if( load_size   ) begin
            size_en    = 1'b1;
          end
  
          pr_resp_type = pr_wr;
          pr_resp_data = 32'b0;
           
        end
        // Read type
        else begin
            pr_resp_type = pr_rd;
            pr_resp_data = 32'b1;
        end
      end
  
      ///////////////////// READR STATE //////////////////////////////////////
  
      if(state_reg == STATE_READR) begin
          // Send Memory Request
          mem_req_val   = 1'b1;
          mem_req_addr  = addr_R;
          mem_req_type  = mem_rd;

          // clear count_G
          count_G_clear = 1'b1; 

          if ( mem_req_go ) begin 
            count_R_en  = 1'b1;
            if ( count_R > 32'b0 ) 
              reg_r1_en[count_G-32'b1] = 1'b1;  
          end

      end
 
      ///////////////////// WAITR STATE //////////////////////////////////////
  
      if(state_reg == STATE_WAITR) begin
          
          // Send Memory Request
          mem_resp_rdy  = 1'b1;
          mem_resp_type = mem_rd;
 
          // Receive Memory Response
          if( mem_resp_go ) begin
            for ( i = 0; i < m; i = i + 1 ) begin
              reg_r0_en[i] = 1'b1;
            end
          end
      end
 
      ///////////////////// READG STATE //////////////////////////////////////
  
      if(state_reg == STATE_READG) begin
          
          // Send Memory Request
          mem_req_val   = 1'b1;
          mem_req_addr  = addr_G;
          mem_req_type  = mem_rd;

          if ( mem_req_go ) begin 
              count_G_en  = 1'b1;

             if ( count_G > 32'b0 ) 
               reg_r1_en[count_G-32'b1] = 1'b1;

          end

      end
 
      ///////////////////// WAITG STATE //////////////////////////////////////
  
      if(state_reg == STATE_WAITG) begin
          
          // Send Memory Request
          mem_resp_rdy  = 1'b1;
          mem_resp_type = mem_rd;
 
          // Receive Memory Response
          if( mem_resp_go ) begin
            for ( i = 0; i < m; i = i + 1 ) begin
              reg_g_en[i] = 1'b1;
            end
          end
      end
 
 
  //    // START STATE
  //    if(state_reg == STATE_START) begin
  //
  //        // Send Memory Request
  //        mem_request   = 1'b1;
  //        mem_addr_d[0] = base_G + 8*counter_G + counter_C*offset;
  //        mem_type_d[0] = 3'b0;
  //        mem_addr_d[1] = base_G + 8*counter_G + counter_C*offset +4;
  //        mem_type_d[1] = 3'b0;
  //        // Receive Memory Response
  //        if(mem_resp_val[0] == 1'b1 && mem_resp_val[1]) begin
  //            if(counter_R == 3'd3) begin
  //                reg_r0_d[counter_R*2]   = mem_resp_data[0];
  //                reg_r0_d[counter_R*2+1] = mem_resp_data[1];
  //                counter_R_d             = counter_R + 3'b1;
  //            end
  //            else begin
  //                reg_g_d[counter_G*2]   = mem_resp_data[0];
  //                reg_g_d[counter_G*2+1] = mem_resp_data[0];
  //                counter_G_d            = counter_G + 3'b1;
  //                counter_R_d            = 3'b0;
  //            end
  //        end
  //    end
  //
  //    // RUN STATE
  //    if(state_reg == STATE_RUN) begin
  //
  //        // Send Memory Request
  //        mem_request   = 1'b1;
  //        if(counter_G_d == 3'd3) begin
  //            mem_addr_d[0] = base_G + counter_C*offset;
  //            mem_addr_d[1] = base_G + counter_C*offset + 4;
  //        end
  //        else begin
  //            mem_addr_d[0] = base_G + 8*counter_G + counter_C*offset;
  //            mem_addr_d[1] = base_G + 8*counter_G + counter_C*offset + 4;
  //        end
  //        mem_type_d[0] = 3'b0;
  //        mem_type_d[1] = 3'b0;
  //        // Receive Memory Response
  //        if(mem_resp_val[0] == 1'b1 && mem_resp_val[1]) begin
  //            if(counter_G == 3'd3) begin
  //                reg_g_d[counter_G*2]   = mem_resp_data[0];
  //                reg_g_d[counter_G*2+1] = mem_resp_data[1];
  //                counter_G_d            = 3'b0;
  //            end
  //            else begin
  //                reg_g_d[counter_G*2]   = mem_resp_data[0];
  //                reg_g_d[counter_G*2+1] = mem_resp_data[0];
  //                counter_G_d            = counter_G + 3'b1;
  //                counter_R_d            = 3'b0;
  //            end
  //            reg_g_d[counter_G*2]   = mem_resp_data[0];
  //            reg_g_d[counter_G*2+1] = mem_resp_data[0];
  //        end
  //        // Send Mapper Request Message
  //
  //    end
  //
  //    // WAIT STATE
  //    if(state_reg == STATE_WAIT) begin
  //
  //        // Send Memory Request
  //        mem_request   = 1'b1;
  //        mem_addr_d[0] = base_G + 8*counter_G + counter_C*offset;
  //        mem_type_d[0] = 3'b0;
  //        mem_addr_d[1] = base_G + 8*counter_G + counter_C*offset +4;
  //        mem_type_d[1] = 3'b0;
  //        // Receive Memory Response
  //        if(mem_resp_val[0] == 1'b1 && mem_resp_val[1]) begin
  //            reg_g_d[counter_G*2]   = mem_resp_data[0];
  //            reg_g_d[counter_G*2+1] = mem_resp_data[0];
  //        end
  //    end
  //
  //    // END STATE
  //    if(state_reg == STATE_END) begin
  //
  //        // stop sending Memory Request
  //        mem_request   = 1'b0;
  //
  //        // Send Mapper Request
  //    end
  //
  //    // WRITE STATE
  //    if(state_reg == STATE_WRITE) begin
  //
  //        // Send Memory Request
  //        mem_request   = 1'b1;
  //        mem_addr_d[0] = base_G + 8*counter_G + counter_C*offset;
  //        mem_data_d[0] = 
  //        mem_type_d[0] = 3'b1;
  //        mem_addr_d[1] = base_G + 8*counter_G + counter_C*offset +4;
  //        mem_data_d[1] = 
  //        mem_type_d[1] = 3'b1;
  //
  //    end
  end
  
    //-----------------------------------------------------------------------
    // Line Tracing
    //-----------------------------------------------------------------------
  
    `ifndef SYNTHESIS
  
    logic [`VC_TRACE_NBITS-1:0] str;
  
    `VC_TRACE_BEGIN
    begin
  
//      $sformat( str, "%x:%x:%x", pr_req_data, pr_req_addr, pr_req_type );
//      vc_trace.append_val_rdy_str( trace_str, pr_req_val, pr_req_rdy, str );
  
//      $sformat( str, " | GRS(%x | %x | %d)", base_G, base_R, size );
//      vc_trace.append_str( trace_str, str );
//      vc_trace.append_str( trace_str, " " );
  
      $sformat( str, "(%d)", count_G );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );

      $sformat( str, "R0(%x|%x|%x|%x)", reg_r0[0], reg_r0[1], reg_r0[2], reg_r0[3] );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );
      $sformat( str, "R1(%d|%d|%d|%d|%d|%d|%d|%d)", reg_r1[0], reg_r1[1], reg_r1[2], reg_r1[3], reg_r1[4], reg_r1[5], reg_r1[6], reg_r1[7] );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );
      $sformat( str, "G(%x|%x|%x|%x)", reg_g[0], reg_g[1], reg_g[2], reg_g[3] );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );


      vc_trace.append_str( trace_str, "(" );
  
      case ( state_reg )
        STATE_INIT:   vc_trace.append_str( trace_str, "INIT " );
        STATE_READR:  vc_trace.append_str( trace_str, "READR" );
        STATE_WAITR:  vc_trace.append_str( trace_str, "WAITR" );
        STATE_READG:  vc_trace.append_str( trace_str, "READG" );
        STATE_WAITG:  vc_trace.append_str( trace_str, "WAITG" );
  
        default:
          vc_trace.append_str( trace_str, "?  " );
  
      endcase
  
      vc_trace.append_str( trace_str, ")" );

 //     $sformat( str, "(%d | %x)", count_R, addr_R );
 //     vc_trace.append_str( trace_str, str );
 //     vc_trace.append_str( trace_str, " " );
 
//      $sformat( str, "req(%x | %x | %x | %d)", mem_req_val, mem_req_rdy, mem_req_addr, mem_req_data );
//      vc_trace.append_str( trace_str, str );
//      vc_trace.append_str( trace_str, " " );
//   
//      $sformat( str, "resp(%x | %x | %d)", mem_resp_val, mem_resp_rdy, mem_resp_data );
//      vc_trace.append_str( trace_str, str );
//      vc_trace.append_str( trace_str, " " );

//      $sformat( str, "%x:%x", pr_resp_data, pr_resp_type );
//      vc_trace.append_val_rdy_str( trace_str, pr_resp_val, pr_resp_rdy, str );
  
    end
    `VC_TRACE_END
  
    `endif /* SYNTHESIS */
  
  
  
endmodule
