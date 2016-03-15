//======================================================================
// SchedulerVRTL
//======================================================================

`include "mem-msgs.v"
`include "pageRank-msgs.v"

`include "trace.v"


module SchedulerVRTL
#(
  parameter nbits  = 8,
  parameter nports = 1,
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

  //----------------------------------------------------------------------- 
  // Registers to store one column of G
  //----------------------------------------------------------------------- 

  // registers
  logic [nbits-1:0] reg_g [0:3];
 
  // wires 
  logic [nbits-1:0] reg_g_d [0:3];

  // wires, wr enable  
  logic             reg_g_en [0:3];

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      for ( i = 0; i < n; i = i + 1 ) begin
        reg_g[i] <= 8'b0;
      end
    end
    else begin
      for ( i = 0; i < n; i = i + 1 ) begin
        if ( reg_g_en[i] == 1'b1 ) 
          reg_g[i] <= reg_g_d[i];
        else 
          reg_g[i] <= reg_g[i];
      end
    end
  end

  //----------------------------------------------------------------------
  // Counters
  //
  // counter_R iterate R
  // counter_G iterate G's column
  // counter_W
  // counter_C
  //----------------------------------------------------------------------

  logic [2:0]  counter_R;
  logic [2:0]  counter_R_d;

  logic [2:0]  counter_G;
  logic [2:0]  counter_G_d;

  logic [2:0]  counter_W;
  logic [2:0]  counter_W_d;

  logic [2:0]  counter_C;
  logic [2:0]  counter_C_d;

  logic [2:0]  offset;
  logic [2:0]  offset_d;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      counter_R <= 3'b0;
      counter_G <= 3'b0;
      counter_W <= 3'b0;
      counter_C <= 3'b0;
      offset    <= 3'b0;
    end
    else begin
      counter_R <= counter_R_d;
      counter_G <= counter_G_d;
      counter_W <= counter_W_d;
      counter_C <= counter_C_d;
      offset    <= offset_d;
    end
  end

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------


  typedef enum logic [$clog2(8)-1:0] {
    STATE_INIT  , 
    STATE_READR , 
    STATE_READG , 
    STATE_RUN   , 
    STATE_WAIT  , 
    STATE_END   , 
    STATE_WRITE  
  } state_t;


  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [2:0] state_reg;
  logic [2:0] state_next;

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

  assign pr_req_go       = pr_req_val  && pr_req_rdy;
  assign pr_resp_go      = pr_resp_val && pr_resp_rdy;

  assign go              = pr_req_go && ( pr_req_type == pr_wr ) && ( pr_req_addr == 32'd0 );

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_INIT:  if ( go        )           state_next = STATE_INIT; 
//      STATE_INIT:   if ( counter_R == 3'd3  )  state_next = STATE_IDLE;
//      STATE_START:  if ( counter_G == 3'd3  )  state_next = STATE_RUN;
//      STATE_RUN:    if ( red_resp_val  )       state_next = STATE_WAIT;
//      STATE_WAIT:   if ( resp_go   )           state_next = STATE_END;  
//      STATE_END:    if ( resp_go   )           state_next = STATE_WRITE;
//      STATE_WRITE:  if ( resp_go   )           state_next = STATE_SOURCE;
      default:    state_next = 'x;

    endcase

  end

  // regs base address of G and R, size
  
  logic [31:0]  base_G;
  logic [31:0]  base_R;
  logic [31:0]  size;
  
  logic         base_G_en;
  logic         base_R_en;
  logic         size_en;
  
  
  always_ff @ (posedge clk) begin
    if ( reset ) begin 
      base_G <= 32'b0;
      base_R <= 32'b0;
      size   <= 32'b0;
    end    
    else if ( base_G_en )
      base_G <= pr_req_data;
    else if ( base_R_en )
      base_R <= pr_req_data;
    else if ( size_en   )
      size   <= pr_req_data;    
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
  
      counter_R_d  = 3'b0;
      counter_G_d  = 3'b0;
      counter_C_d  = 3'b0;
      counter_W_d  = 3'b0;
      offset_d     = 3'b0;
  
      /////////////////////////  INIT STATE    ///////////////////////////////////
  
      if( state_reg == STATE_INIT ) begin
  
        pr_req_rdy  = pr_resp_rdy;
        pr_resp_val = pr_req_val;
  
        // Write tpye
        if ( pr_req_type == pr_wr ) begin
          if ( go ) begin
            // Send the first memory req
            mem_req_val  = 1'b1;
            mem_req_addr = base_R;
            mem_req_type = mem_rd;
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
  
  //    ///////////////////// READR STATE //////////////////////////////////////
  //
  //    if(state_reg == STATE_SOURCE) begin
  //
  //        // Send Memory Request
  //        mem_req_val   = 1'b1;
  //        mem_addr      = base_R + 8*counter_R;
  //        mem_type      = 3'b0;
  //
  //        // Receive Memory Response
  //        if( memresp_go ) begin
  //            reg_r0_d[counter_R*2]   = mem_resp_data[0];
  //            reg_r0_d[counter_R*2+1] = mem_resp_data[1];
  //            counter_R_d             = counter_R + 3'b1;
  //        end
  //    end
  //
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
  
      $sformat( str, "%x:%x:%x", pr_req_data, pr_req_addr, pr_req_type );
      vc_trace.append_val_rdy_str( trace_str, pr_req_val, pr_req_rdy, str );
  
      $sformat( str, " | GRS(%x | %x | %d)", base_G, base_R, size );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );
  
      vc_trace.append_str( trace_str, "(" );
  
      case ( state_reg )
        STATE_INIT:
          vc_trace.append_str( trace_str, "INIT" );
  
        default:
          vc_trace.append_str( trace_str, "?  " );
  
      endcase
  
      vc_trace.append_str( trace_str, ")" );
  
      $sformat( str, "%x:%x", pr_resp_data, pr_resp_type );
      vc_trace.append_val_rdy_str( trace_str, pr_resp_val, pr_resp_rdy, str );
  
    end
    `VC_TRACE_END
  
    `endif /* SYNTHESIS */
  
  
  
endmodule
