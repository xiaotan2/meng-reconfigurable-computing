#====================================================================
# Mapper
#====================================================================
from pymtl      import *
from pclib.rtl  import EqComparator, RegEnRst, RegRst
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from MapperMsg  import MapperReqMsg, MapperRespMsg

#====================================================================
# Mapper Datapath
#====================================================================
class MapperDpathPRTL( Model ):

  # Constructor
  def __init__( s, nbits = 8, mbits = 1 ):
    
    # Interface
    s.req_msg_data  = InPort (nbits)
    s.req_msg_type  = InPort (mbits)
    s.resp_msg_data = Output (nbits)
    s.resp_msg_type = Output (mbits)

    s.reference_data  = Wire( Bits(nbits) )
 
    # Register for reference data     
    s.Reg_reference_data = m = RegEnRst( nbits )
    s.connect_dict({
      m.en  : s.req_msg_type,
      m.in_ : s.req_msg_data,
      m.out : s.reference_data,
    })

    # Zero comparator
    s.EqComparator_1 = m = EqComparator( nbits )
    s.connect_dict({
      m.in0 : s.req_msg_data,
      m.in1 : s.reference_data,
      m.out : s.resp_msg_data,
    })

    s.connect( s.resp_msg_type, s.req_msg_type )


#====================================================================
# Mapper Control Unit
#====================================================================
class MapperCtrlPRTL( Model ):
  
  # Constructor
  def __init__( s ):

    # Interface
    s.req_val  = Inport  (1)
    s.req_rdy  = Outport (1)

    s.resp_val = OutPort (1)
    s.resp_rdy = InPort  (1)

    s.STATE_IDLE  = 0 
    s.STATE_CMP   = 1 # do compare or store reference data

    s.state = RegRst( 1, reset_value = s.STATE_IDLE )

    #------------------------------------------------------
    # state transtion logic
    #------------------------------------------------------

    @s.combinational
    def state_transitions():
    
      curr_state = s.state.out
      next_state = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        if ( s.req_val and s.req_rdy ):
          next_state = s.STATE_CMP

      if ( curr_state == s.STATE_CMP ):
        if ( s.resp_val and s.resp_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state


    #------------------------------------------------------
    # state output logic
    #------------------------------------------------------
  
    @s.combinational
    def state_outputs():
      
      current_state = s.state.out

      if ( current_state == s.STATE_IDLE ):
        s.req_rdy.value = 1
        s.resp_val.value = 0
        
      elif ( current_state == s.STATE_CMP ):
        s.req_rdy.value = 0
        s.resp_val.value = 1
 



#====================================================================
# Mapper Top Level
#====================================================================
class MapperPRTL( Model ):

  # Constructor
  def __init__( s, nbits = 8, mbits = 1 ):
    
    # Interface
    s.req  = InValRdyBundle  ( MapperReqMsg()  ) 
    s.resp = OutValRdyBundle ( MapperRespMsg() )

    # Instantiate datapath and control
    s.dpath = MapperDpathPRTL( nbits, mbits )
    s.ctrl  = MapperCtrlPRTL()

    # connect input interface to dpath/ctrl
    s.connect( s.req.msg.data,      s.dpath.req_msg_data  )
    s.connect( s.req.msg.type,      s.dpath.req_msg_type  )

    s.connect( s.req.val,           s.ctrl.req_val        )
    s.connect( s.resp.rdy,          s.ctrl.resp_rdy       )
 
    # connect dpath/ctrl to output interface
    s.connect( s.resp.msg.data,     s.dpath.resp_msg_data )
    s.connect( s.resp.msg.type,     s.dpath.resp_msg_type )

    s.connect( s.req.rdy,           s.ctrl.req_rdy        )
    s.connect( s.resp.val,          s.ctrl.resp_val       )


  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I"
    if s.ctrl.state.out == s.ctrl.STATE_CMP:
      state_str = "CMP"

    return "{}({} {} {}){}".format(
      s.req,
      s.dpath.reference_data,
      s.dpath.resp_msg_data,
      s.state_str,
      s.resp
    }

