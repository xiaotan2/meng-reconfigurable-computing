//------------------------------------------------------------------------
// SortXcelHLS
//------------------------------------------------------------------------

void SortXcelHLS
(
  hls::stream<XcelReqMsg>&  xcelreq,
  hls::stream<XcelRespMsg>& xcelresp,
  MemReqType&  memreq,
  MemRespType& memresp
){
  // Local variables
  XcelReqMsg  req;

  // 1. Write the base address of the array to xr1
  req = xcelreq.read();
  ap_uint<32> base = req.data;
  xcelresp.write( XcelRespMsg( req.id, 0, req.type, req.opq ) );

  // 2. Write the number of elements in the array to xr2
  req = xcelreq.read();
  ap_uint<32> size = req.data;
  xcelresp.write( XcelRespMsg( req.id, 0, req.type, req.opq ) );

  // 3. Tell accelerator to go by writing xr0
  while ( xcelreq.empty() );
  req = xcelreq.read();
  xcelresp.write( XcelRespMsg( req.id, 0, req.type, req.opq ) );

  // Compute
  sort( ArrayMemPortAdapter( base, size, memreq, memresp ) );

  // 4. Wait for accelerator to finish by reading xr0, result will be 1
  req = xcelreq.read();
  xcelresp.write( XcelRespMsg( req.id, 1, req.type, req.opq ) );
}

template < typename Array >
void sort( Array array )
{
  int n = array.size();
  for ( int i = 0; i < n; ++i ) {
    int prev = array[0];

    for ( int j = 1; j < n; ++j ) {
      int curr = array[j];
      array[j-1] = std::min( prev, curr );
      prev       = std::max( prev, curr );
    }

		array[n-1] = prev;
	}
