OpenCL Matrix Multiplication Example
================================

This is an implementation of performing matrix multiplication of two 16x16 matrices and getting the result back in 16x16 matrix. 
The main algorithm characteristics of this application are:

1.	The matrices are flattened out in a single dimension before sending it to FPGA, so the kernel operates the matrix multiplication under that assumption.
2.	The example is parameterized, so it can be increased to larger size. 
3.	This is a starter example to illustrate the use flow of SDAccel. Users may need to modify their source code when multiplying very large matrices. 

Compiling the Application
---------------------------
This application is compiled using the SDAccel script mode target to alpha-data 7v3 platform.

To compile the application:
sdaccel example_alphadata.tcl

The target board can be changed by editing *example_alphadata.tcl*

Executing the Application
---------------------------
mmult1

The above steps can also be performed through the Makefile flow

Files in the Example
---------------------
Application host code
- test-cl.c

Kernel code
- mmult1.cl

Compilation Script
- example_alphadata.tcl
