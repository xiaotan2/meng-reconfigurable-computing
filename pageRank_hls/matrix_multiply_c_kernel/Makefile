FLAGS = -std=c99

all: sparseMatrix

# Compile & run digitrec implementation
sparseMatrix: genSparseMatrix.cpp
	@echo "Compiling & executing the sparse matrix program ..."
	g++ ${CFLAGS} genSparseMatrix.cpp -o genSparseMatrix
	./genSparseMatrix
