#include "test-cl.h"
#include <stdio.h>
#define P_VALUE 0.15

// Helper Functions
void sparseMatrixMul(float* result,  float* A,  int* IA,  int* JA, float* R) {
  // initialize result to 0
  for(int i = 0; i < MATRIX_RANK; ++i) {
    result[i] = 0;
  }
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

void vectorAdd( float* rank_vector, float* V1, float* V2) {
  for(int i = 0; i < MATRIX_RANK; ++i) {
    rank_vector[i] = V1[i] + V2[i];
  }
}

// PageRank
void pageRank( float* rank_vector,  float* A,  int* IA,  int* JA){
    /*printf("A:\n");
    for (int i = 0; i < A_SIZE; i++) {
        printf("%f, ", A[i]); 
    }
    printf("\n ");
    printf("IA:\n");
    for (int i =0; i < IA_SIZE; i++) {
    printf("%d, ", IA[i]);
    }
    printf("\n");
    printf("JA:\n");
    for (int i = 0; i < JA_SIZE; i++) {
    printf("%d, ", JA[i]);
    }
    printf("\n");*/

  // Initialize row_vector to 1/MATRIX_RANK
  float row_vector[MATRIX_RANK];
  for (int i = 0; i < MATRIX_RANK; ++i)
    row_vector[i] = 1/(float)(MATRIX_RANK);  

  /*printf("Row Vector:\n");
  for (int i = 0; i < MATRIX_RANK; i++)
    printf("%f, ", row_vector[i]); 
  printf("\n");*/

  // Initialize rank_vector to 0
  for (int j = 0; j < MATRIX_RANK; ++j)
    rank_vector[j] = 0;  

  float error = 10000;
  float threshold = 0.001;
  float vector1[MATRIX_RANK];
  float vector2[MATRIX_RANK];
  
  for ( int idx = 0; error > threshold; ++idx ){ //error > threshold ; ++idx ){
    /*printf("Initial RowVector Result:\n");
    for (int i = 0; i < MATRIX_RANK; i++) {
      printf("%f, ", row_vector[i]);
    }
    printf("\n");*/
    sparseMatrixMul(vector1, A, IA, JA, row_vector);
    /*printf("SparseMatrixMul Result:\n");
    for (int i = 0; i < MATRIX_RANK; i++) {
      printf("%f, ", vector1[i]);
    }
    printf("\n");*/
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
    /*printf("Final RowVector Result:\n");
    for (int i = 0; i < MATRIX_RANK; i++) {
      printf("%f, ", row_vector[i]);
    }
    printf("\n");*/
  }
}

int main()
{
   float bufoutput[MATRIX_RANK] = {0,0,0,0,0};

  pageRank(bufoutput, A, IA, JA);

  printf("Final Output\n");
  for (int i = 0; i < MATRIX_RANK; i++)
    printf("%f, ",bufoutput[i]);
  printf("\n");
  return 0;
}



