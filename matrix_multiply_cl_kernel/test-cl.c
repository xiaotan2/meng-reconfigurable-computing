/*******************************************************************************
Vendor: Xilinx 
Associated Filename: test-cl.c
Purpose: OpenCL Host Code for Matrix Multiply Example
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
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <assert.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <CL/opencl.h>

////////////////////////////// Sparse Matrix Data //////////////////////////////
#include "test-cl.h"   
  
#define P_VALUE 0.15

////////////////////////////////////////////////////////////////////////////////
//                         Testing Helper Functions                           //
// /////////////////////////////////////////////////////////////////////////////
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


////////////////////////////////////////////////////////////////////////////////

int
load_file_to_memory(const char *filename, char **result)
{ 
    size_t size = 0;
    FILE *f = fopen(filename, "rb");
    if (f == NULL) 
        { 
            *result = NULL;
            return -1; // -1 means file opening fail 
        } 
    fseek(f, 0, SEEK_END);
    size = ftell(f);
    fseek(f, 0, SEEK_SET);
    *result = (char *)malloc(size+1);
    if (size != fread(*result, sizeof(char), size, f)) 
        { 
            free(*result);
            return -2; // -2 means file reading fail 
        } 
    fclose(f);
    (*result)[size] = 0;
    return size;
}

int main(int argc, char** argv)
{
    //Change the line below for your target device
    char target_device_name[1001] = "xilinx:adm-pcie-7v3:1ddr:2.1";

    int err;                            // error code returned from api calls
//    int a[DATA_SIZE];                   // original data set given to device
//    int b[DATA_SIZE];                   // original data set given to device
    float results[MATRIX_RANK];         // results returned from device
    float sw_results[MATRIX_RANK];        // results returned from device
    unsigned int correct;               // number of correct results returned

    size_t global[2];                   // global domain size for our calculation
    size_t local[2];                    // local domain size for our calculation

    cl_platform_id platforms[16];       // platform id
    cl_platform_id platform_id;         // platform id
    cl_uint platform_count;
    cl_device_id device_id;             // compute device id 
    cl_context context;                 // compute context
    cl_command_queue commands;          // compute command queue
    cl_program program;                 // compute program
    cl_kernel kernel;                   // compute kernel
   
    char cl_platform_vendor[1001];
    char cl_platform_name[1001];

    cl_mem input_A;                     // device memory used for the input array
    cl_mem input_IA;                    // device memory used for the input array
    cl_mem input_JA;                    // device memory used for the input array
    cl_mem output;                      // device memory used for the output array
   
    if (argc != 2){
        printf("%s <inputfile>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // Initialize results to all zeros
    int i = 0;
    for(i = 0; i < MATRIX_RANK; i++) {
        sw_results[i] = 0;
        results[i] = 0;
    }

    // 
    // Get all platforms and then select Xilinx platform
    err = clGetPlatformIDs(16, platforms, &platform_count);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to find an OpenCL platform!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }
    printf("INFO: Found %d platforms\n", platform_count);

    // Find Xilinx Plaftorm
    int platform_found = 0;
    for (unsigned int iplat=0; iplat<platform_count; iplat++) {
        err = clGetPlatformInfo(platforms[iplat], CL_PLATFORM_VENDOR, 1000, (void *)cl_platform_vendor,NULL);
        if (err != CL_SUCCESS) {
            printf("Error: clGetPlatformInfo(CL_PLATFORM_VENDOR) failed!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }
        if (strcmp(cl_platform_vendor, "Xilinx") == 0) {
            printf("INFO: Selected platform %d from %s\n", iplat, cl_platform_vendor);
            platform_id = platforms[iplat];
            platform_found = 1;
        }
    }
    if (!platform_found) {
        printf("ERROR: Platform Xilinx not found. Exit.\n");
        return EXIT_FAILURE;
    }
  
    // Connect to a compute device
    // find all devices and then select the target device
    cl_device_id devices[16];  // compute device id 
    cl_uint device_count;
    unsigned int device_found = 0;
    char cl_device_name[1001];
    err = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_ACCELERATOR,
                         16, devices, &device_count);
    if (err != CL_SUCCESS) {
        printf("Error: Failed to create a device group!\n");
        printf("Test failed\n");
        return EXIT_FAILURE;
    }

    //iterate all devices to select the target device. 
    for (int i=0; i<device_count; i++) {
        err = clGetDeviceInfo(devices[i], CL_DEVICE_NAME, 1024, cl_device_name, 0);
        if (err != CL_SUCCESS) {
            printf("Error: Failed to get device name for device %d!\n", i);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }
        //printf("CL_DEVICE_NAME %s\n", cl_device_name);
        if(strcmp(cl_device_name, target_device_name) == 0) {
            device_id = devices[i];
            device_found = 1;
            printf("INFO: Selected %s as the target device\n", cl_device_name);
        }
    }
    
    if (!device_found) {
        printf("ERROR: Target device %s not found. Exit.\n", target_device_name);
        return EXIT_FAILURE;
    }


    err = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_ACCELERATOR,
                         1, &device_id, NULL);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to create a device group!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }
  
    // Create a compute context 
    //
    context = clCreateContext(0, 1, &device_id, NULL, NULL, &err);
    if (!context)
        {
            printf("Error: Failed to create a compute context!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Create a command commands
    //
    commands = clCreateCommandQueue(context, device_id, 0, &err);
    if (!commands)
        {
            printf("Error: Failed to create a command commands!\n");
            printf("Error: code %i\n",err);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    int status;

    // Create Program Objects
    //
  
    // Load binary from disk
    unsigned char *kernelbinary;
    char *xclbin=argv[1];
    printf("INFO: Loading %s\n", xclbin);
    int n_i = load_file_to_memory(xclbin, (char **) &kernelbinary);
    if (n_i < 0) {
        printf("failed to load kernel from xclbin: %s\n", xclbin);
        printf("Test failed\n");
        return EXIT_FAILURE;
    }
    size_t n = n_i;
    // Create the compute program from offline
    program = clCreateProgramWithBinary(context, 1, &device_id, &n,
                                        (const unsigned char **) &kernelbinary, &status, &err);
    if ((!program) || (err!=CL_SUCCESS)) {
        printf("Error: Failed to create compute program from binary %d!\n", err);
        printf("Test failed\n");
        return EXIT_FAILURE;
    }

    // Build the program executable
    //
    err = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
    if (err != CL_SUCCESS)
        {
            size_t len;
            char buffer[2048];

            printf("Error: Failed to build program executable!\n");
            clGetProgramBuildInfo(program, device_id, CL_PROGRAM_BUILD_LOG, sizeof(buffer), buffer, &len);
            printf("%s\n", buffer);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Create the compute kernel in the program we wish to run
    //
    kernel = clCreateKernel(program, "mmult", &err);
    if (!kernel || err != CL_SUCCESS)
        {
            printf("Error: Failed to create compute kernel!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Create the input and output arrays in device memory for our calculation
    //
    input_A  = clCreateBuffer(context,  CL_MEM_READ_ONLY,  sizeof(float) * A_SIZE,      NULL, NULL);
    input_IA = clCreateBuffer(context,  CL_MEM_READ_ONLY,  sizeof(int)   * IA_SIZE,     NULL, NULL);
    input_JA = clCreateBuffer(context,  CL_MEM_READ_ONLY,  sizeof(int)   * JA_SIZE,     NULL, NULL);
    output   = clCreateBuffer(context,  CL_MEM_WRITE_ONLY, sizeof(float) * MATRIX_RANK, NULL, NULL);

    if ( !input_A || !input_IA || !input_JA || !output )
        {
            printf("Error: Failed to allocate device memory!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }    
    
    // Write our data set into the input array in device memory 
    //
    err = clEnqueueWriteBuffer(commands, input_A, CL_TRUE, 0, sizeof(float) * A_SIZE, A, 0, NULL, NULL);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to write to source array A!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Write our data set into the input array in device memory 
    //
    err = clEnqueueWriteBuffer(commands, input_IA, CL_TRUE, 0, sizeof(int) * IA_SIZE, IA, 0, NULL, NULL);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to write to source array IA!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Write our data set into the input array in device memory 
    //
    err = clEnqueueWriteBuffer(commands, input_JA, CL_TRUE, 0, sizeof(int) * JA_SIZE, JA, 0, NULL, NULL);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to write to source array JA!\n");
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    
    // Set the arguments to our compute kernel
    //
    err = 0;
    err  = clSetKernelArg(kernel, 0, sizeof(cl_mem), &input_A);
    err |= clSetKernelArg(kernel, 1, sizeof(cl_mem), &input_IA);
    err |= clSetKernelArg(kernel, 2, sizeof(cl_mem), &input_JA);
    err |= clSetKernelArg(kernel, 3, sizeof(cl_mem), &output);
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to set kernel arguments! %d\n", err);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Execute the kernel over the entire range of our 1d input data set
    // using the maximum number of work group items for this device
    //

#ifdef C_KERNEL
    err = clEnqueueTask(commands, kernel, 0, NULL, NULL);
#else
    global[0] = 1;
    global[1] = 1;
    local[0]  = 1;
    local[1]  = 1;
    err = clEnqueueNDRangeKernel(commands, kernel, 2, NULL, 
                                 (size_t*)&global, (size_t*)&local, 0, NULL, NULL);
#endif
    if (err)
        {
            printf("Error: Failed to execute kernel! %d\n", err);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    // Read back the results from the device to verify the output
    //
    cl_event readevent;
    err = clEnqueueReadBuffer( commands, output, CL_TRUE, 0, sizeof(float) * MATRIX_RANK, results, 0, NULL, &readevent );  
    if (err != CL_SUCCESS)
        {
            printf("Error: Failed to read output array! %d\n", err);
            printf("Test failed\n");
            return EXIT_FAILURE;
        }

    clWaitForEvents(1, &readevent);
    
    printf("A\n");
    for (i=0;i<A_SIZE;i++) {
        printf("%f ",A[i]);
    }
    printf("\n");

    printf("IA\n");
    for (i=0;i<IA_SIZE;i++) {
        printf("%d ",IA[i]);
    }
    printf("\n");

    printf("JA\n");
    for (i=0;i<JA_SIZE;i++) {
        printf("%d ",JA[i]);
    }
    printf("\n");

    printf("RES\n");
    for (i=0;i<MATRIX_RANK;i++) {
        printf("%.25f ",results[i]);
    }
    printf("\n");
    

    // //////////////////////////////////////////////////////////////////////////////
    // run software pagerank for verification ///////////////////////////////////////
    // //////////////////////////////////////////////////////////////////////////////
    //
    pageRank(sw_results, A, IA, JA);

    printf("SW_RES\n");
    correct = 0;
    for ( int i = 0; i < MATRIX_RANK; i++) {
      printf("%.25f ", sw_results[i]);
      if (sw_results[i] == results[i])
        correct++;
    }
    /*
    FILE *fp;
    fp = fopen("results.txt", "w");
    
    if (fp == NULL){
      printf("Error opening file\n");
      exit(1);
    }
    
    for (i=0;i<MATRIX_RANK;i++)
      fprintf(fp, "%.25f\n", results[i]);
    
    fclose(fp);
    */

    // Shutdown and cleanup
    //
    clReleaseMemObject(input_A);
    clReleaseMemObject(input_IA);
    clReleaseMemObject(input_JA);
    clReleaseMemObject(output);
    clReleaseProgram(program);
    clReleaseKernel(kernel);
    clReleaseCommandQueue(commands);
    clReleaseContext(context);

    if(correct == MATRIX_RANK){
        printf("Test passed!\n");
        return EXIT_SUCCESS;
    }
    else{
        printf("Test failed\n");
        return EXIT_FAILURE;
    }
}

// XSIP watermark, do not delete 67d7842dbbe25473c3c32b93c0da8047785f30d78e8a024de1b57352245f9689
