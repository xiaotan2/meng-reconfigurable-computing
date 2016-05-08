FLAGS = -std=c99

all: mm sparseMatrix

# Compile & run digitrec implementation
mm: mmult1_native.c
	@echo "Compiling & executing the sparse matrix program ..."
	gcc ${FLAGS} mmult1_native.c -o mmult1_native
	./mmult1_native

# Compile & run digitrec implementation
sparseMatrix: genSparseMatrix.cpp
	@echo "Compiling & executing the sparse matrix program ..."
	g++ genSparseMatrix.cpp -o genSparseMatrix
	./genSparseMatrix
