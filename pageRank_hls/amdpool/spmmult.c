#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define P_VALUE 0.15
float* pageRank(int nodes, float* A, int* IA, int* JA);

int main(int nodes, float* A, int* IA, int* JA, float* output)
{
#pragma HLS INTERFACE m_axi port=nodes offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=A offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=IA offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=JA offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=gmem
#pragma HLS INTERFACE s_axilite port=nodes bundle=control
#pragma HLS INTERFACE s_axilite port=A bundle=control
#pragma HLS INTERFACE s_axilite port=IA bundle=control
#pragma HLS INTERFACE s_axilite port=JA bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    float* output_buf = pageRank(nodes, A, IA, JA);
    memcpy ((void*)output, (void*)output_buf, nodes*sizeof(float));
    return -1;
}

// Helper Functions
float* sparseMatrixMul(float* A, int* IA, int* JA, float* R, int nodes) {
  // Initialize result to 0
  float* result = (float*)malloc(sizeof(float)*nodes);
  for (int j = 0; j < nodes; ++j)
    result[j] = 0;

  for(int i = 0; i < nodes; ++i) {
    for(int k = IA[i]; k < IA[i+1]; ++k) {
      result[i] = result[i] + A[k] * R[JA[k]];
    }
    result[i] *= (1-P_VALUE);
  }
  return result;
}

float* vectorMul(float* V, float value, int nodes) {
  // Initialize result to 0
  float* result = (float*)malloc(sizeof(float)*nodes);
  for (int j = 0; j < nodes; ++j)
    result[j] = 0;

  for(int i = 0; i < nodes; ++i) {
    result[i] = V[i]*value;
  }
  return result;
}

float* vectorAdd(float* V1, float* V2, int nodes) {
  // Initialize result to 0
  float* result = (float*)malloc(sizeof(float)*nodes);
  for (int j = 0; j < nodes; ++j)
    result[j] = 0;

  for(int i = 0; i < nodes; ++i) {
    result[i] = V1[i] + V2[i];
  }
  return result;
}


// PageRank
float* pageRank(int nodes, float* A, int* IA, int* JA){
 
  // Initialize row_vector to 1/nodes
  float row_vector[nodes];
  for (int i = 0; i < nodes; ++i)
    row_vector[i] = 1/(float)(nodes);  

  // Initialize rank_vector to 0
  float* rank_vector = (float*)malloc(sizeof(float)*nodes);
  for (int j = 0; j < nodes; ++j)
    rank_vector[j] = 0;  


  float error = 10000;
  float threshold = 0.001;

  for ( int idx = 0; error > threshold ; ++idx ){
    float* vector1 = sparseMatrixMul(A, IA, JA, row_vector, nodes);
    float* vector2 = vectorMul(row_vector, P_VALUE, nodes);
    rank_vector = vectorAdd(vector1, vector2, nodes);

    // Error Calculation
    error = 0;
    for ( int i = 0; i < nodes; ++i )
      error += abs(rank_vector[i] - row_vector[i]); 

    memcpy((void*)row_vector, (void*)rank_vector, sizeof(float)*nodes);
  }

  for ( int i = 0; i < nodes; ++i )
    printf("%f ", rank_vector[i] ); 
  
  return rank_vector;


}
