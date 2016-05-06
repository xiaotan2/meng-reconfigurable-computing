#include "test-cl.h"
#define P_VALUE 0.15

// Helper Functions
void sparseMatrixMul(float* result, __local float* A, __local int* IA, __local int* JA, float* R) {
  for(int i = 0; i < MATRIX_RANK; ++i) {
    for(int k = IA[i]; k < IA[i+1]; ++k) {
      result[i] = result[i] + A[k] * R[JA[k]];
    }
    result[i] *= (1-P_VALUE);
  }
}

void vectorMul(float* result, float* V, float value) {
  for(int i = 0; i < MATRIX_RANK; ++i) {
    result[i] = V[i]*value;
  }
}

void vectorAdd(__local float* rank_vector, float* V1, float* V2) {
  for(int i = 0; i < MATRIX_RANK; ++i) {
    rank_vector[i] = V1[i] + V2[i];
  }
}

// PageRank
void pageRank(__local float* rank_vector, __local float* A, __local int* IA, __local int* JA){
 
  // Initialize row_vector to 1/MATRIX_RANK
  float row_vector[MATRIX_RANK];
  for (int i = 0; i < MATRIX_RANK; ++i)
    row_vector[i] = 1/(float)(MATRIX_RANK);  

  // Initialize rank_vector to 0
  for (int j = 0; j < MATRIX_RANK; ++j)
    rank_vector[j] = 0;  

  float error = 10000;
  float threshold = 0.1;
  float vector1[MATRIX_RANK];
  float vector2[MATRIX_RANK];
  
  for ( int idx = 0; idx < 2; idx++ ){ //error > threshold ; ++idx ){
    sparseMatrixMul(vector1, A, IA, JA, row_vector);
    vectorMul(vector2, row_vector, P_VALUE);
    vectorAdd(rank_vector, vector1, vector2);

    // Error Calculation
    error = 0;
    for ( int i = 0; i < MATRIX_RANK; ++i ) {
      if ( (rank_vector[i] - row_vector[i]) < 0 )
        error += row_vector[i] - rank_vector[i];
      else
        error += rank_vector[i] - row_vector[i]; 
    }
    for ( int i = 0; i < MATRIX_RANK; ++i ){
      row_vector[i] = rank_vector[i];
    }
  }
}


__kernel __attribute__ ((reqd_work_group_size(1, 1, 1)))
void mmult(__global float* A, __global int* IA, __global int* JA, __global float* output)
{
  __local float bufA[A_SIZE];
  __local int   bufIA[IA_SIZE];
  __local int   bufJA[JA_SIZE];
  __local float bufoutput[MATRIX_RANK];
  event_t e0, e1, e2, e3;

  e0 = async_work_group_copy(bufA, A, A_SIZE, 0);
  e1 = async_work_group_copy(bufIA, IA, IA_SIZE, 0);
  e2 = async_work_group_copy(bufJA, JA, JA_SIZE, 0);
  wait_group_events(1, &e0);
  wait_group_events(1, &e1);
  wait_group_events(1, &e2);

  for (unsigned int i = 0; i < MATRIX_RANK; i++){
    bufoutput[i] = bufA[i];
  }

  pageRank(bufoutput, bufA, bufIA, bufJA);
  e3 = async_work_group_copy(output, bufoutput, MATRIX_RANK, 0);
  wait_group_events(1, &e3);

  return;
}



