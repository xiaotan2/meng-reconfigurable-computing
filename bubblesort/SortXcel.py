#===========================================================================================

from pymtl      import *
from pclib.ifcs import XcelMsg, MemMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle  

class SortXcel(Model):

  def __init__(s):

    #Interface
    #sink or source
    s.xcelreq  = InValRdyBundle( XcelReqMsg() )
    s.xcelresp = OutValRdyBundle( XcelRespMsg() )

    #memory
    s.memreq  = OutValRdyBundle( MemReqMsg() )
    s.memresp = InValRdyBundle( MemRespMsg() )


    # Queues
    s.xcelreq_q = SingleElementBypassQueue( XcelReqMsg() )
    s.connect( s.xcelreq, s.xcelreq_q.enq )

    s.memreq_q = SingleElementBypassQueue( MemReqMsg(8,32,32) )
    s.connect( s.memreq, s.memreq_q.deq )

    s.memresp_q = SingleElementBypassQueue( MemRespMsg(8,32) )
    s.connect( s.memresp, s.memresp_q.enq )


class SortXcelCtrl(Model):

  def __init__(s):

    #Interface
    #sink or source
    s.xcelreq_val  = InPort(1)
    s.xcelreq_rdy  = OutPort(1)
    s.xcelresp_val = OutPort(1)
    s.xcelresp_rdy = InPort(1)

    #memory
    s.memreq_val  = OutPort(1)
    s.memreq_rdy  = InPort(1)
    s.memresp_val = InPort(1)
    s.memresp_rdy = OutPort(1)


    # Control signals (ctrl->dpath)


    # Status signals (dpath->ctrl)



class SortXcelDpath(Model):

  def __init__(s):


