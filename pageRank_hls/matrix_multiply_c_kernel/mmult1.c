/*******************************************************************************
Vendor: Xilinx 
Associated Filename: mmult1.c
Purpose: HLS C matrix multiply kernel example
Revision History: July 1, 2013 - initial release
                                                
*******************************************************************************
Copyright (C) 2013 XILINX, Inc.

This file contains confidential and proprietary information of Xilinx, Inc. and 
is protected under U.S. and international copyright and other intellectual 
property laws.

DISCLAIMER
This disclaimer is not a license and does not grant any rights to the materials 
distributed herewith. Except as otherwise provided in a valid license issued to 
you by Xilinx, and to the maximum extent permitted by applicable law: 
(1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND WITH ALL FAULTS, AND XILINX 
HEREBY DISCLAIMS ALL WARRANTIES AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, 
INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-INFRINGEMENT, OR 
FITNESS FOR ANY PARTICULAR PURPOSE; and (2) Xilinx shall not be liable (whether 
in contract or tort, including negligence, or under any other theory of 
liability) for any loss or damage of any kind or nature related to, arising under 
or in connection with these materials, including for any direct, or any indirect, 
special, incidental, or consequential loss or damage (including loss of data, 
profits, goodwill, or any type of loss or damage suffered as a result of any 
action brought by a third party) even if such damage or loss was reasonably 
foreseeable or Xilinx had been advised of the possibility of the same.

CRITICAL APPLICATIONS
Xilinx products are not designed or intended to be fail-safe, or for use in any 
application requiring fail-safe performance, such as life-support or safety 
devices or systems, Class III medical devices, nuclear facilities, applications 
related to the deployment of airbags, or any other applications that could lead 
to death, personal injury, or severe property or environmental damage 
(individually and collectively, "Critical Applications"). Customer assumes the 
sole risk and liability of any use of Xilinx products in Critical Applications, 
subject only to applicable laws and regulations governing limitations on product 
liability. 

THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS PART OF THIS FILE AT 
ALL TIMES.

*******************************************************************************/

#include <string.h>
#include "test-cl.h"

//#include <stdlib.h>
//#include <stdio.h>
#define P_VALUE 0.15

float* pageRank(int nodes, float* A, int* IA, int* JA);

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


void mmult(float* A, int* IA, int* JA, float* output)
{
#pragma HLS INTERFACE m_axi port=A      offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=IA     offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=JA     offset=slave bundle=gmem
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=gmem
#pragma HLS INTERFACE s_axilite port=A      bundle=control
#pragma HLS INTERFACE s_axilite port=IA     bundle=control
#pragma HLS INTERFACE s_axilite port=JA     bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

  float bufA[A_SIZE];
  int   bufIA[IA_SIZE];
  int   bufJA[JA_SIZE];
  float bufoutput[MATRIX_RANK];

  memcpy(bufA,  (float *) A,  A_SIZE*sizeof(float));
  memcpy(bufIA, (int   *) IA, IA_SIZE*sizeof(int) );
  memcpy(bufJA, (int   *) JA, JA_SIZE*sizeof(int) );
  
  for (unsigned int i = 0; i < MATRIX_RANK; i++){
    bufoutput[i] = bufA[i];
  }

  // float* output_buf = pageRank(nodes, A, IA, JA);
  memcpy((float *) output, bufoutput, MATRIX_RANK*sizeof(float));
  return;
}


// XSIP watermark, do not delete 67d7842dbbe25473c3c32b93c0da8047785f30d78e8a024de1b57352245f9689

