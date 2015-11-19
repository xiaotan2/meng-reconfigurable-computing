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
class MapperDpathRTL( Model ):

  # Constructor
  def __init__( s, nbits = 8, mbits = 1 ):
    
    # Interface
    s.req_msg_data      = InPort  (nbits)
    s.resp_msg_data     = OutPort (  1  )
    
    s.result_reg_en     = InPort  (  1  )
    s.reference_reg_en  = InPort  (  1  )

    s.reference_data  = Wire( Bits(nbits) )
    s.cmp_result      = Wire( Bits(  1  ) )

    # Register for reference data     
    s.Reg_reference_data = m = RegEnRst( nbits )
    s.connect_dict({
      m.en  : s.reference_reg_en,
      m.in_ : s.req_msg_data,
      m.out : s.reference_data,
    })

    # Zero comparator
    s.EqComparator_1 = m = EqComparator( nbits )
    s.connect_dict({
      m.in0 : s.req_msg_data,
      m.in1 : s.reference_data,
      m.out : s.cmp_result,
    })

    # Register for compare result     
    s.Reg_cmp_result = m = RegEnRst( 1 )
    s.connect_dict({
      m.en  : s.result_reg_en,
      m.in_ : s.cmp_result,
      m.out : s.resp_msg_data,
    })
   


#====================================================================
# Mapper Control Unit
#====================================================================
class MapperCtrlRTL( Model ):
  
  # Constructor
  def __init__( s, mbits = 1 ):

    # Interface
    s.req_val          = InPort  (1)
    s.req_rdy          = OutPort (1)

    s.resp_val         = OutPort (1)
    s.resp_rdy         = InPort  (1)

    s.req_msg_type     = InPort  (mbits)
    s.resp_msg_type    = OutPort (mbits)

    s.result_reg_en    = OutPort(1)
    s.reference_reg_en = OutPort(1)


    s.msg_type_reg_en = Wire ( Bits(1) )

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
        s.req_rdy.value          = 1
        s.resp_val.value         = 0
        s.result_reg_en.value    = 1
        s.reference_reg_en.value = s.req_msg_type
        s.msg_type_reg_en.value  = 1
        
      elif ( current_state == s.STATE_CMP ):
        s.req_rdy.value          = 0
        s.resp_val.value         = 1
        s.result_reg_en.value    = 0
        s.reference_reg_en.value = 0
        s.msg_type_reg_en.value  = 0

    # Register for resp msg type     
    s.Reg_msg_type = m = RegEnRst( 1 )
    s.connect_dict({
      m.en  : s.msg_type_reg_en,
      m.in_ : s.req_msg_type,
      m.out : s.resp_msg_type,
    })


#====================================================================
# Mapper Top Level
#====================================================================
class MapperRTL( Model ):

  # Constructor
  def __init__( s, nbits = 8, mbits = 1 ):
    
    # Interface
    s.req  = InValRdyBundle  ( MapperReqMsg()  ) 
    s.resp = OutValRdyBundle ( MapperRespMsg() )

    # Instantiate datapath and control
    s.dpath = MapperDpathRTL( nbits, mbits )
    s.ctrl  = MapperCtrlRTL ( mbits )

    # connect input interface to dpath/ctrl
    s.connect( s.req.msg.data,      s.dpath.req_msg_data  )

    s.connect( s.req.msg.type_,     s.ctrl.req_msg_type   )
    s.connect( s.req.val,           s.ctrl.req_val        )
    s.connect( s.resp.rdy,          s.ctrl.resp_rdy       )
 
    # connect dpath/ctrl to output interface
    s.connect( s.dpath.resp_msg_data,  s.resp.msg.data    )
                                                          
    s.connect( s.ctrl.resp_msg_type,  s.resp.msg.type_    )
    s.connect( s.ctrl.req_rdy,        s.req.rdy           )
    s.connect( s.ctrl.resp_val,       s.resp.val          )

    # connect dpath/ctrl
    s.connect( s.ctrl.result_reg_en,    s.dpath.result_reg_en    )
    s.connect( s.ctrl.reference_reg_en, s.dpath.reference_reg_en )

  def line_trace( s ):

    state_str = "?  "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "I  "
    if s.ctrl.state.out == s.ctrl.STATE_CMP:
      state_str = "CMP"

    return "{} ({} {}=?{}->{} {}) {}".format(
      s.req,
      s.ctrl.req_msg_type,
      s.dpath.reference_data,
      s.dpath.req_msg_data,
      s.dpath.resp_msg_data,
      state_str,
      s.resp
    )

