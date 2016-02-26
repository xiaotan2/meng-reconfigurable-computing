//==========================================================================
// pageRankMsgs
//==========================================================================

//-------------------------------------------------------------------------------
//  pageRank request message
//  +---------+-----------------------+--------------------+
//  |type_[64]| addr[63:32]           | data[31:0]         |
//  +---------+-----------------------+--------------------+
//-------------------------------------------------------------------------------

// define field from right to left
// data
`define PAGERANK_REQ_MSG_DATA_NBITS(t_,a_,d_)  \
  d_

`define PAGERANK_REQ_MSG_DATA_MSB(t_,a_,d_)    \
  ( `PAGERANK_REQ_MSG_DATA_NBITS(t_,a_,d_)-1 )

`define PAGERANK_REQ_MSG_DATA_FIELD(t_,a_,d_)  \
  ( `PAGERANK_REQ_MSG_DATA_MSB(t_,a_,d_) ) :   \
  0

// address
`define PAGERANK_REQ_MSG_ADDR_NBITS(t_,a_,d_)  \
  a_

`define PAGERANK_REQ_MSG_ADDR_MSB(t_,a_,d_)    \
  ( `PAGERANK_REQ_MSG_DATA_MSB(t_,a_,d_)       \
  + `PAGERANK_REQ_MSG_ADDR_NBITS(t_,a_,d_) )

`define PAGERANK_REQ_MSG_ADDR_FIELD(t_,a_,d_)  \
  ( `PAGERANK_REQ_MSG_ADDR_MSB(t_,a_,d_) ) :   \
  ( `PAGERANK_REQ_MSG_DATA_MSB(t_,a_,d_) + 1) 
  

// type
`define PAGERANK_REQ_MSG_TYPE_NBITS(t_,a_,d_)  \
  t_

`define PAGERANK_REQ_MSG_TYPE_MSB(t_,a_,d_)    \
  ( `PAGERANK_REQ_MSG_ADDR_MSB(t_,a_,d_)       \
  + `PAGERANK_REQ_MSG_TYPE_NBITS(t_,a_,d_) )

`define PAGERANK_REQ_MSG_TYPE_FIELD(t_,a_,d_)  \
  ( `PAGERANK_REQ_MSG_TYPE_MSB(t_,a_,d_) ) :   \
  ( `PAGERANK_REQ_MSG_ADDR_MSB(t_,a_,d_) + 1) 
  
`define PAGERANK_REQ_MSG_TYPE_READ  0
`define PAGERANK_REQ_MSG_TYPE_WRITE 1

// Total size of message
`define PAGERANK_REQ_MSG_NBITS(t_,a_,d_)      \
  (   `PAGERANK_REQ_MSG_TYPE_NBITS(t_,a_,d_)  \
    + `PAGERANK_REQ_MSG_ADDR_NBITS(t_,a_,d_)  \
    + `PAGERANK_REQ_MSG_DATA_NBITS(t_,a_,d_) )

//----------------------------------------------------------------------------
// PageRank Request Msg Pack
//----------------------------------------------------------------------------

module pageRankReqMsgPack
#(
  parameter p_type_nbits = 1,
  parameter p_addr_nbits = 32,
  parameter p_data_nbits = 32,

  // short name for message type
  parameter t = p_type_nbits,
  parameter a = p_addr_nbits,
  parameter d = p_data_nbits
)(

  input  logic [`PAGERANK_REQ_MSG_TYPE_NBITS(t,a,d)-1:0] type_,
  input  logic [`PAGERANK_REQ_MSG_ADDR_NBITS(t,a,d)-1:0] addr,
  input  logic [`PAGERANK_REQ_MSG_DATA_NBITS(t,a,d)-1:0] data,

  output logic [`PAGERANK_REQ_MSG_NBITS(t,a,d)-1:0] msg
);

  assign msg[`PAGERANK_REQ_MSG_TYPE_FIELD(t,a,d)] = type_;
  assign msg[`PAGERANK_REQ_MSG_ADDR_FIELD(t,a,d)] = addr;
  assign msg[`PAGERANK_REQ_MSG_DATA_FIELD(t,a,d)] = data;
  
endmodule


//----------------------------------------------------------------------------
// PageRank Request Unpack Msg
//----------------------------------------------------------------------------

module pageRankReqMsgUnpack
#(
  parameter p_type_nbits = 1,
  parameter p_addr_nbits = 32,
  parameter p_data_nbits = 32,

  // short name for message type
  parameter t = p_type_nbits,
  parameter a = p_addr_nbits,
  parameter d = p_data_nbits
) (

  // input bits
  input logic [`PAGERANK_REQ_MSG_NBITS(t,a,d)-1:0]  msg,

  // output message
  
  output  logic [`PAGERANK_REQ_MSG_TYPE_NBITS(t,a,d)-1:0] type_,
  output  logic [`PAGERANK_REQ_MSG_ADDR_NBITS(t,a,d)-1:0] addr,
  output  logic [`PAGERANK_REQ_MSG_DATA_NBITS(t,a,d)-1:0] data
);

  assign type_ = msg[`PAGERANK_REQ_MSG_TYPE_FIELD(t,a,d)];
  assign addr  = msg[`PAGERANK_REQ_MSG_ADDR_FIELD(t,a,d)];
  assign data  = msg[`PAGERANK_REQ_MSG_DATA_FIELD(t,a,d)];

endmodule

//-------------------------------------------------------------------------------
//  pageRank response message
//  +---------+-----------------------+
//  |type_[64]| data[31:0]            |
//  +---------+-----------------------+
//-------------------------------------------------------------------------------

// define field from right to left
// data
`define PAGERANK_RESP_MSG_DATA_NBITS(t_,d_)  \
  d_

`define PAGERANK_RESP_MSG_DATA_MSB(t_,d_)    \
  ( `PAGERANK_RESP_MSG_DATA_NBITS(t_,d_)-1 )

`define PAGERANK_RESP_MSG_DATA_FIELD(t_,d_)  \
  ( `PAGERANK_RESP_MSG_DATA_MSB(t_,d_) ) :   \
  0

// type
`define PAGERANK_RESP_MSG_TYPE_NBITS(t_,d_)  \
  t_

`define PAGERANK_RESP_MSG_TYPE_MSB(t_,d_)    \
  ( `PAGERANK_RESP_MSG_DATA_MSB(t_,d_)       \
  + `PAGERANK_RESP_MSG_TYPE_NBITS(t_,d_) )

`define PAGERANK_RESP_MSG_TYPE_FIELD(t_,d_)  \
  ( `PAGERANK_RESP_MSG_TYPE_MSB(t_,d_) ) :   \
  ( `PAGERANK_RESP_MSG_DATA_MSB(t_,d_) + 1) 
  
`define PAGERANK_RESP_MSG_TYPE_READ  0
`define PAGERANK_RESP_MSG_TYPE_WRITE 1

// Total size of message
`define PAGERANK_RESP_MSG_NBITS(t_,d_)      \
  (   `PAGERANK_RESP_MSG_TYPE_NBITS(t_,d_)  \
    + `PAGERANK_RESP_MSG_DATA_NBITS(t_,d_) )

//----------------------------------------------------------------------------
// PageRank Response Msg Pack
//----------------------------------------------------------------------------

module pageRankRespMsgPack
#(
  parameter p_type_nbits = 1,
  parameter p_data_nbits = 32,

  // short name for message type
  parameter t = p_type_nbits,
  parameter d = p_data_nbits
)(

  input  logic [`PAGERANK_RESP_MSG_TYPE_NBITS(t,d)-1:0] type_,
  input  logic [`PAGERANK_RESP_MSG_DATA_NBITS(t,d)-1:0] data,

  output logic [`PAGERANK_RESP_MSG_NBITS(t,d)-1:0] msg
);

  assign msg[`PAGERANK_RESP_MSG_TYPE_FIELD(t,d)] = type_;
  assign msg[`PAGERANK_RESP_MSG_DATA_FIELD(t,d)] = data;
  
endmodule


//----------------------------------------------------------------------------
// PageRank Response Unpack Msg
//----------------------------------------------------------------------------

module pageRankRespMsgUnpack
#(
  parameter p_type_nbits = 1,
  parameter p_data_nbits = 32,

  // short name for message type
  parameter t = p_type_nbits,
  parameter d = p_data_nbits
) (

  // input bits
  input logic [`PAGERANK_RESP_MSG_NBITS(t,d)-1:0]  msg,

  // output message
  
  output  logic [`PAGERANK_RESP_MSG_TYPE_NBITS(t,d)-1:0] type_,
  output  logic [`PAGERANK_RESP_MSG_DATA_NBITS(t,d)-1:0] data
);

  assign type_ = msg[`PAGERANK_RESP_MSG_TYPE_FIELD(t,d)];
  assign data  = msg[`PAGERANK_RESP_MSG_DATA_FIELD(t,d)];

endmodule
