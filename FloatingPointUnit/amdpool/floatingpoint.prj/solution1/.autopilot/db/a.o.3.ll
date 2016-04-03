; ModuleID = '/home/student/xt85/MENG/meng-reconfigurable-computing/FloatingPointUnit/amdpool/floatingpoint.prj/solution1/.autopilot/db/a.o.3.bc'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@llvm_global_ctors_1 = appending global [1 x void ()*] [void ()* @_GLOBAL__I_a] ; [#uses=0 type=[1 x void ()*]*]
@llvm_global_ctors_0 = appending global [1 x i32] [i32 65535] ; [#uses=0 type=[1 x i32]*]
@cpp_float_str = internal unnamed_addr constant [10 x i8] c"cpp_float\00" ; [#uses=1 type=[10 x i8]*]

; [#uses=4]
declare void @llvm.dbg.value(metadata, i64, metadata) nounwind readnone

; [#uses=0]
define float @cpp_float(float %a, float %b) nounwind uwtable readnone {
  call void (...)* @_ssdm_op_SpecBitsMap(float %a) nounwind, !map !7
  call void (...)* @_ssdm_op_SpecBitsMap(float %b) nounwind, !map !13
  call void (...)* @_ssdm_op_SpecBitsMap(float 0.000000e+00) nounwind, !map !17
  call void (...)* @_ssdm_op_SpecTopModule([10 x i8]* @cpp_float_str) nounwind
  %b_read = call float @_ssdm_op_Read.ap_auto.float(float %b) nounwind ; [#uses=1 type=float]
  call void @llvm.dbg.value(metadata !{float %b_read}, i64 0, metadata !23), !dbg !32 ; [debug line = 10:36] [debug variable = b]
  %a_read = call float @_ssdm_op_Read.ap_auto.float(float %a) nounwind ; [#uses=1 type=float]
  call void @llvm.dbg.value(metadata !{float %a_read}, i64 0, metadata !33), !dbg !34 ; [debug line = 10:26] [debug variable = a]
  call void @llvm.dbg.value(metadata !{float %a}, i64 0, metadata !33), !dbg !34 ; [debug line = 10:26] [debug variable = a]
  call void @llvm.dbg.value(metadata !{float %b}, i64 0, metadata !23), !dbg !32 ; [debug line = 10:36] [debug variable = b]
  %tmp = fadd float %a_read, %b_read, !dbg !35    ; [#uses=1 type=float] [debug line = 12:3]
  ret float %tmp, !dbg !35                        ; [debug line = 12:3]
}

; [#uses=1]
define weak void @_ssdm_op_SpecTopModule(...) {
entry:
  ret void
}

; [#uses=3]
define weak void @_ssdm_op_SpecBitsMap(...) {
entry:
  ret void
}

; [#uses=2]
define weak float @_ssdm_op_Read.ap_auto.float(float) {
entry:
  ret float %0
}

; [#uses=0]
declare i16 @_ssdm_op_HSub(...)

; [#uses=0]
declare i16 @_ssdm_op_HMul(...)

; [#uses=0]
declare i16 @_ssdm_op_HDiv(...)

; [#uses=0]
declare i16 @_ssdm_op_HAdd(...)

; [#uses=1]
declare void @_GLOBAL__I_a() nounwind section ".text.startup"

!hls.encrypted.func = !{}
!llvm.map.gv = !{!0}

!0 = metadata !{metadata !1, [1 x i32]* @llvm_global_ctors_0}
!1 = metadata !{metadata !2}
!2 = metadata !{i32 0, i32 31, metadata !3}
!3 = metadata !{metadata !4}
!4 = metadata !{metadata !"llvm.global_ctors.0", metadata !5, metadata !"", i32 0, i32 31}
!5 = metadata !{metadata !6}
!6 = metadata !{i32 0, i32 0, i32 1}
!7 = metadata !{metadata !8}
!8 = metadata !{i32 0, i32 31, metadata !9}
!9 = metadata !{metadata !10}
!10 = metadata !{metadata !"a", metadata !11, metadata !"float", i32 0, i32 31}
!11 = metadata !{metadata !12}
!12 = metadata !{i32 0, i32 0, i32 0}
!13 = metadata !{metadata !14}
!14 = metadata !{i32 0, i32 31, metadata !15}
!15 = metadata !{metadata !16}
!16 = metadata !{metadata !"b", metadata !11, metadata !"float", i32 0, i32 31}
!17 = metadata !{metadata !18}
!18 = metadata !{i32 0, i32 31, metadata !19}
!19 = metadata !{metadata !20}
!20 = metadata !{metadata !"return", metadata !21, metadata !"data_t", i32 0, i32 31}
!21 = metadata !{metadata !22}
!22 = metadata !{i32 0, i32 1, i32 0}
!23 = metadata !{i32 786689, metadata !24, metadata !"b", metadata !25, i32 33554442, metadata !28, i32 0, i32 0} ; [ DW_TAG_arg_variable ]
!24 = metadata !{i32 786478, i32 0, metadata !25, metadata !"cpp_float", metadata !"cpp_float", metadata !"_Z9cpp_floatff", metadata !25, i32 10, metadata !26, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 false, float (float, float)* @cpp_float, null, null, metadata !30, i32 10} ; [ DW_TAG_subprogram ]
!25 = metadata !{i32 786473, metadata !"floatingpoint.cpp", metadata !"/home/student/xt85/MENG/meng-reconfigurable-computing/FloatingPointUnit/amdpool", null} ; [ DW_TAG_file_type ]
!26 = metadata !{i32 786453, i32 0, metadata !"", i32 0, i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !27, i32 0, i32 0} ; [ DW_TAG_subroutine_type ]
!27 = metadata !{metadata !28, metadata !28, metadata !28}
!28 = metadata !{i32 786454, null, metadata !"data_t", metadata !25, i32 10, i64 0, i64 0, i64 0, i32 0, metadata !29} ; [ DW_TAG_typedef ]
!29 = metadata !{i32 786468, null, metadata !"float", null, i32 0, i64 32, i64 32, i64 0, i32 0, i32 4} ; [ DW_TAG_base_type ]
!30 = metadata !{metadata !31}
!31 = metadata !{i32 786468}                      ; [ DW_TAG_base_type ]
!32 = metadata !{i32 10, i32 36, metadata !24, null}
!33 = metadata !{i32 786689, metadata !24, metadata !"a", metadata !25, i32 16777226, metadata !28, i32 0, i32 0} ; [ DW_TAG_arg_variable ]
!34 = metadata !{i32 10, i32 26, metadata !24, null}
!35 = metadata !{i32 12, i32 3, metadata !36, null}
!36 = metadata !{i32 786443, metadata !24, i32 10, i32 40, metadata !25, i32 0} ; [ DW_TAG_lexical_block ]
