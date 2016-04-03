; ModuleID = '/home/student/xt85/MENG/meng-reconfigurable-computing/FloatingPointUnit/amdpool/floatingpoint.prj/solution1/.autopilot/db/a.o.2.bc'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@llvm_global_ctors_1 = appending global [1 x void ()*] [void ()* @_GLOBAL__I_a]
@llvm_global_ctors_0 = appending global [1 x i32] [i32 65535]
@cpp_float_str = internal unnamed_addr constant [10 x i8] c"cpp_float\00"

declare void @llvm.dbg.value(metadata, i64, metadata) nounwind readnone

define float @cpp_float(float %a, float %b) nounwind uwtable readnone {
  call void (...)* @_ssdm_op_SpecBitsMap(float %a) nounwind, !map !7
  call void (...)* @_ssdm_op_SpecBitsMap(float %b) nounwind, !map !13
  call void (...)* @_ssdm_op_SpecBitsMap(float 0.000000e+00) nounwind, !map !17
  call void (...)* @_ssdm_op_SpecTopModule([10 x i8]* @cpp_float_str) nounwind
  %b_read = call float @_ssdm_op_Read.ap_auto.float(float %b) nounwind
  %a_read = call float @_ssdm_op_Read.ap_auto.float(float %a) nounwind
  %tmp = fadd float %a_read, %b_read
  ret float %tmp
}

define weak void @_ssdm_op_SpecTopModule(...) {
entry:
  ret void
}

define weak void @_ssdm_op_SpecBitsMap(...) {
entry:
  ret void
}

define weak float @_ssdm_op_Read.ap_auto.float(float) {
entry:
  ret float %0
}

declare i16 @_ssdm_op_HSub(...)

declare i16 @_ssdm_op_HMul(...)

declare i16 @_ssdm_op_HDiv(...)

declare i16 @_ssdm_op_HAdd(...)

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
