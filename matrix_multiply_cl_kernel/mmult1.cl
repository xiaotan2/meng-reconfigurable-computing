#include "test-cl.h"
#define P_VALUE 0.15

// Helper Functions
void sparseMatrixMul(__local float* result, __local float* A, __local int* IA, __local int* JA, __local float* R) {
  int lid = get_local_id(0);
  result[lid] = 0;
  for(int k = IA[lid]; k < IA[lid+1]; ++k) {
    result[lid] = result[lid] + A[k] * R[JA[k]];
  }
  result[lid] *= (1-P_VALUE);
}


__kernel __attribute__ ((reqd_work_group_size(MATRIX_RANK, 1, 1)))
void mmult(__global float* A, __global int* IA, __global int* JA, __global float* output)
{
  __local float bufA[A_SIZE];
  __local int   bufIA[IA_SIZE];
  __local int   bufJA[JA_SIZE];
  __local float bufR[MATRIX_RANK];
  __local float bufoutput[MATRIX_RANK];
  event_t e0, e1, e2, e3, e4;

  e0 = async_work_group_copy(bufA, A, A_SIZE, 0);
  e1 = async_work_group_copy(bufIA, IA, IA_SIZE, 0);
  e2 = async_work_group_copy(bufJA, JA, JA_SIZE, 0);
  e3 = async_work_group_copy(bufR, output, MATRIX_RANK, 0);
  wait_group_events(1, &e0);
  wait_group_events(1, &e1);
  wait_group_events(1, &e2);
  wait_group_events(1, &e3);

  sparseMatrixMul(bufoutput, bufA, bufIA, bufJA, bufR);
  barrier(CLK_LOCAL_MEM_FENCE);
  e4 = async_work_group_copy(output, bufoutput, MATRIX_RANK, 0);
  wait_group_events(1, &e4);

  return;
}



