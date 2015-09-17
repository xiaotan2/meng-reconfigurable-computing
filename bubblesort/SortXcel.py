#===========================================================================================

from pymtl      import *
from pclib.ifcs import XcelMsg, MemMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle  

class SortXcel(Model):

  def __init__(s):

    #Interface
    #sink or source
    s.xcelreq  = InValRdyBundle( XcelReqMsg() );
    s.xcelresp = OutValRdyBundle( XcelRespMsg() );
    s.xcelreq_val  = InPort(1);
    s.xcelreq_rdy  = OutPort(1);
    s.xcelresp_val = OutPort(1);
    s.xcelresp_rdy = InPort(1);
    #s.xcelreq.raddr s.xcelreq.data (write)
    #s.xcelresp.data (read)

    #memory
    s.mem.reqs  = OutValRdyBundle( MemReqMsg() );
    s.mem.resps = InValRdyBundle( MemRespMsg() );
    s.mem.reqs_val  = InPort(1);
    s.mem.reqs_rdy  = OutPort(1);
    s.mem.resps_val = OutPort(1);
    s.mem.resps_rdy = InPort(1);
    #s.mem.reqs.addr s.mem.reqs.data (write)
    #s.mem.resps.data (read)


