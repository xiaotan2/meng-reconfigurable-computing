//========================================================================
// ListInsertHLS.cc
//========================================================================

#include "polydsu_list/ListInsertHLS.h"

//-------------------------------------------------------------------
// list::insert
// Note that the real insert function would allocate its own memory,
// and take in iterators as arguments
//-------------------------------------------------------------------
List::iterator insert( List::const_iterator pos,
                       List::iterator::pointer new_node,
                       const Type& val )
{
  List::iterator::pointer p = pos.get_ptr();

  new_node->m_value = val;
  new_node->m_next = p;
  new_node->m_prev = p->m_prev;

  p->m_prev->m_next = new_node;
  p->m_prev = new_node;
  return List::iterator(new_node);
}

//-------------------------------------------------------------------
// HLS top function
// We write this in a way such that any of the arch. registers
// can be configured in any order
// Address Map:
//   1 - base pointer of the node to insert at
//   2 - base pointer of the node to be inserted
//   3 - value to be inserted
//-------------------------------------------------------------------
void ListInsertHLS(
  hls::stream<xcel::XcelReqMsg>&  xcelreq,
  hls::stream<xcel::XcelRespMsg>& xcelresp,
  xmem::MemReqStream&             memreq,
  xmem::MemRespStream&            memresp
){
  // architectural registers
  typedef ap_uint<32> DataType;
  static DataType s_ptr_at;
  static DataType s_ptr_toinsert;
  static DataType s_val;
  static DataType s_result;

  xcel::XcelReqMsg req = xcelreq.read();
  ap_uint<32> addr = req.addr();

  if (req.type() == xcel::XcelReqMsg::TYPE_WRITE) {

    switch (addr) {
      case 0:
        /*printf ("starting work!\n");
        printf ("  ptr_at : %u!\n", s_ptr_at.to_uint());
        printf ("  ptr_toins : %u!\n", s_ptr_toinsert.to_uint());
        printf ("  val : %u!\n", s_val.to_uint());*/

        s_result = insert(
            List::const_iterator( 
              List::iterator::pointer( s_ptr_at, req.opq(), memreq, memresp )
            ),
            List::iterator::pointer( s_ptr_toinsert, req.opq(), memreq, memresp ),
            s_val
        ).get_ptr().get_addr();
        break;
      case 1:
        s_ptr_at = req.data();        break;
      case 2:
        s_ptr_toinsert = req.data();  break;
      case 3:
        s_val = req.data();           break;
      default:
        break;
    }

    xcelresp.write( xcel::XcelRespMsg( req.opq(), req.type(), 0, req.id() ) );
  }
  else {
    DataType data = 0;

    switch (addr) {
      case 0:
        data = s_result;        break;
      case 1:
        data = s_ptr_at;        break;
      case 2:
        data = s_ptr_toinsert;  break;
      case 3:
        data = s_val;           break;
      default:
        break;
    }

    xcelresp.write( xcel::XcelRespMsg( req.opq(), req.type(), data, req.id() ) );
  }
}

