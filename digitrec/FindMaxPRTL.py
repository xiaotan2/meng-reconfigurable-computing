#====================================================================
# FindMax
#====================================================================
from pymtl      import *
from pclib.rtl  import EqComparator, RegEnRst, RegRst
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from MapperMsg  import MapperReqMsg, MapperRespMsg

#====================================================================
# FindMax Datapath
#====================================================================
class FindMaxDpathRTL( Model ):

  # Constructor
  def __init__( s, nbits = 6, k = 3 ):
    
    # Interface
    s.req_msg_data     = InPort  (nbits)
    s.resp_msg_data    = OutPort (nbits)
    s.resp_msg_idx     = OutPort ( int( math.ceil( math.log( k , 2 ) ) ) ) 
    
    # dpath->ctrl
    s.isLarger         = OutPort  (1)

    # ctrl->dapth
    s.knn_reg_en       = InPort (1)
    s.max_reg_en       = InPort (1)
    s.idx_reg_en       = InPort (1)
    s.knn_mux_sel      = InPort (1)
    s.knn_count        = InPort ( int( math.ceil( math.log( k , 2 ) ) ) ) # max 3
 

    # knn register     
    s.knn_data0        = Wire( Bits(nbits) )
    
    s.knn_reg = m = RegEnRst( nbits )
    s.connect_dict({
      m.en  : s.knn_reg_en,
      m.in_ : s.req_msg_data,
      m.out : s.knn_data0
    })

    # knn Mux    
    s.knn_data1        = Wire( Bits(nbits) )

    s.knn_mux = m = Mux( nbits, 2 )
    s.connect_dict({
      m.sel     : s.knn_mux_sel,
      m.in_[0]  : s.req_msg_data,
      m.in_[1]  : s.knn_data1
    })

    # Greater than comparator
    s.knn_GtComparator = m = GtComparator( nbits )
    s.connect_dict({
      m.in0 : s.knn_data0,
      m.in1 : s.knn_data1,
      m.out : s.isLarger
    })

    # Max Reg     
    s.max_reg = m = RegEnRst( nbits )
    s.connect_dict({
      m.en  : s.max_reg_en,
      m.in_ : s.knn_data0,
      m.out : s.resp_msg_data
    })
   
    # Idx Reg     
    s.idx_reg = m = RegEnRst(  int( math.ceil( math.log( k , 2 ) ) ) ) # max 2
    s.connect_dict({
      m.en  : s.idx_reg_en,
      m.in_ : s.knn_count,
      m.out : s.resp_msg_idx
    })

#====================================================================
# FindMax Control Unit
#====================================================================
class FindMaxCtrlRTL( Model ):
  
  # Constructor
  def __init__( s, nbits = 6, k = 3 ):

    # Interface
    s.req_val          = InPort  (1)
    s.req_rdy          = OutPort (1)

    s.resp_val         = OutPort (1)
    s.resp_rdy         = InPort  (1)

    # dpath->ctrl
    s.isLarger         = InPort  (1)

    # ctrl->dapth
    s.knn_reg_en       = OutPort (1)
    s.max_reg_en       = OutPort (1)
    s.idx_reg_en       = OutPort (1)
    s.knn_mux_sel      = OutPort (1)
    s.knn_count        = OutPort ( int( math.ceil( math.log( k , 2 ) ) ) ) # max 3

    # internal signal
    s.count_go         = Wire( Bits(1) )

    # states
    s.STATE_IDLE  = 0 
    s.STATE_CMP   = 1 # do compare or store reference data
    s.STATE_DONE  = 2 # return max value and its index

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )
  
    # Counters
    s.knn_count  = Wire ( int( math.ceil( math.log( k, 2) ) ) ) # max 3

    @s.tick
    def counter():
      if ( s.count_go == 1 ):
        s.knn_count.next = s.knn_count + 1
      else:
        s.knn_count.next = 0
  
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
        if ( s.knn_count == k - 1 ):
          next_state = s.STATE_DONE

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

      if   ( current_state == s.STATE_IDLE ):
        s.req_rdy.value     = 1
        s.resp_val.value    = 0

        s.knn_reg_en.value  = 1 
        s.max_reg_en.value  = 0
        s.idx_reg_en.value  = 0
        s.knn_mux_sel.value = 0
        s.count_go.value    = 0

      elif ( current_state == s.STATE_CMP  ):
        s.req_rdy.value     = 0
        s.resp_val.value    = 0
        s.count_go.value    = 1
        
        if ( s.knn_count == 0 ):
          s.knn_reg_en.value  = 1 
          s.knn_mux_sel.value = 0
          s.idx_reg_en.value  = 1
          s.max_reg_en.value  = 1
        
        elif ( s.knn_count == 1 ):
          s.knn_reg_en.value  = 1 
          s.knn_mux_sel.value = 1
          if ( s.isLarger == 1):
            s.idx_reg_en.value  = 1
            s.max_reg_en.value  = 1
          else:
            s.idx_reg_en.value  = 0
            s.max_reg_en.value  = 0
        
        elif ( s.knn_count == 2 ):
          s.knn_reg_en.value  = 0 
          s.knn_mux_sel.value = 1
          if ( s.isLarger == 1):
            s.idx_reg_en.value  = 1
            s.max_reg_en.value  = 1
          else:
            s.idx_reg_en.value  = 0
            s.max_reg_en.value  = 0


      elif ( current_state == s.STATE_DONE ):
        s.req_rdy.value     = 0
        s.resp_val.value    = 1

        s.knn_reg_en.value  = 0
        s.max_reg_en.value  = 0
        s.idx_reg_en.value  = 0
        s.knn_mux_sel.value = 0
        s.count_go.value    = 0



#====================================================================
# FindMax Top Level
#====================================================================
class FindMaxPRTL( Model ):

  # Constructor
  def __init__( s, nbits = 6, k = 3 ):
    
    # Interface
    s.req  = InValRdyBundle  ( FindMaxReqMsg()  ) 
    s.resp = OutValRdyBundle ( FindMaxRespMsg() )

    # Instantiate datapath and control
    s.dpath = FindMaxDpathRTL( nbits, k = 3 )
    s.ctrl  = FindMaxCtrlRTL ( nbits, k = 3 )

    # connect input interface to dpath/ctrl
    s.connect( s.req.msg.data,      s.dpath.req_msg_data  )

    s.connect( s.req.val,           s.ctrl.req_val        )
    s.connect( s.resp.rdy,          s.ctrl.resp_rdy       )
 
    # connect dpath/ctrl to output interface
    s.connect( s.dpath.resp_msg_data,  s.resp.msg.data    )
    s.connect( s.dpath.resp_msg_idx,   s.resp.msg.idx     )                                                      
    
    s.connect( s.ctrl.req_rdy,        s.req.rdy           )
    s.connect( s.ctrl.resp_val,       s.resp.val          )

    # connect dpath/ctrl
    s.connect_auto( s.dapth, s.ctrl )

  def line_trace( s ):

    state_str = "?  "
    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      state_str = "IDLE"
    if s.ctrl.state.out == s.ctrl.STATE_CMP  :
      state_str = "CMP "
    if s.ctrl.state.out == s.ctrl.STATE_DONE :
      state_str = "DONE"

    return "{} ({} {}=?{}->{} {}) {}".format(
      s.req,
      s.ctrl.req_msg_type,
      s.dpath.reference_data,
      s.dpath.req_msg_data,
      s.dpath.resp_msg_data,
      state_str,
      s.resp
    )

