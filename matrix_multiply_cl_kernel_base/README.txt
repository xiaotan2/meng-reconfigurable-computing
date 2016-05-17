OpenCL Matrix Multiplication Example
================================

This is an implementation of performing matrix multiplication of two 16x16 matrices and getting the result back in 16x16 matrix. 
The main algorithm characteristics of this application are:

1.	The matrices are flattened out in a single dimension before sending it to FPGA, so the kernel operates the matrix multiplication under that assumption.
2.	The example is parameterized, so it can be increased to larger size. 
3.	This is a starter example to illustrate the use flow of SDAccel. Users may need to modify their source code when multiplying very large matrices. 


Setup Environment and Run Applications
---------------------------

(1) Add the license path:

export XILINXD_LICENSE_FILE=/work/zhang/common/tools/xilinx/SDAccel/SDAccel-zhang01-eth0-20150818.lic

(2) Source setup script

source /work/zhang/common/tools/xilinx/SDAccel/2015.4/settings64.sh

(3) Compile the application

sdaccel example_alphadata.tcl
reports can be found in example_alpha/rpt/

(4) FPGA (Make sure no pkg/ on the server already)

scp -r example_alpha/pkg yz882@zhang-precision-01.ece.cornell.edu:~
ssh yz882@zhang-precision-01.ece.cornell.edu
Password: 12345
source install.sh
source setup.sh
./example_alpha.exe mmult1.xclbin
reports can be found in sdaccel_profile_summary.csv sdaccel_profile_summary.html


Files
---------------------------
(1) The path to SDAccel 2015.4 on zhang-01 is 

/work/zhang/common/tools/xilinx/SDAccel/2015.4/

(2) Examples directory

/work/zhang/common/tools/xilinx/SDAccel/2015.4/examples



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
