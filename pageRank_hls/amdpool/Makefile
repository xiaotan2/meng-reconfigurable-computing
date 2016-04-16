#==========================================================================
# Makefile
#==========================================================================
# @brief: A makefile the compiles and synthesizes the pageRank program
#
# @desc: 1. "make" runs tmatrix by default
#        2. "make csim" compiles & executes the floating point implementation
#        3. "make clean" cleans up the directory


# Extract Vivado HLS include path
VHLS_PATH := $(dir $(shell which vivado_hls))/..
VHLS_INC ?= ${VHLS_PATH}/include

CFLAGS = -g -I${VHLS_INC} 

all: sparseMatrix


# Compile & run digitrec implementation
sparseMatrix: sparseMatrix.cpp
	@echo "Compiling & executing the sparse matrix program ..."
	g++ ${CFLAGS} sparseMatrix.cpp -o sparseMatrix
	./sparseMatrix

# Compile & run digitrec implementation
tmatrix:tmatrix.cpp
	@echo "Compiling & executing the transition matrix program ..."
	g++ ${CFLAGS} tmatrix.cpp -o tmatrix
	./tmatrix

csim: pageRank.cpp pageRank_test.cpp
	@echo "Compiling & simulating PAGERANK ..."
	g++ ${CFLAGS} $^ -o pageRank
	./pageRank

bitstream: 
	@echo "Synthesizing PAGERANK and creating bitstream ..."
	vivado_hls -f run.tcl
	./run_bitstream.sh

clean:
	@echo "Clean up ..."
	rm -rf pageRank tmatrix *.dat *.prj *.log
	rm -rf zedboard_project* xillydemo.bit
