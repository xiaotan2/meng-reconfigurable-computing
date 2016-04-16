//=========================================================================
// tmatrix.cpp
//=========================================================================
// @brief : A program calculates the transition matrix for a graph in adjacency list format.

#include "tmatrix.h"

#include <cmath>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <iterator>

int main()
{
  // Read input file of the graph in adjacency list format
  std::string line;
  std::ifstream myfile("data/graphs.dat");

  //--------------------------------------------------------------------------------------
  // construct the link matrix
  //--------------------------------------------------------------------------------------

  int size;
  std::vector< std::vector<int> > link_matrix;

  if ( myfile.is_open() ){

    // read first line, get total number of nodes in the graph
    std::getline( myfile, line ); 
    std::stringstream stream( line );
    stream >> size;
    std::cout << "size = " << size << "\n";

    // initialize link_matrix size x size
    link_matrix.resize(size);
    for ( int i = 0; i < size; ++i )
      link_matrix[i].resize(size);

    int row = 0;
    while ( std::getline( myfile, line ) ){
      std::stringstream stream( line );

      std::vector<int> values( (std::istream_iterator<int>(stream)), (std::istream_iterator<int>()) );

//      std::cout << "array of int \n";
      std::vector<int>::iterator value = values.begin();
      value++; // first is the source node
      for ( value; value != values.end(); ++value ) {
        int col = *value;
//        std::cout << col << "\n"; 
        link_matrix[row][col] = link_matrix[row][col] + 1;
      }

      row++;
    }

  }
  else {
    std::cout << "Unable to open the file";
  }

  std::cout << "link_matrix:" << std::endl;
  for ( int i = 0; i < size; ++i ) {
    for ( int j = 0; j < size; ++j ) {
      std::cout << link_matrix[i][j] << " ";
    }
    std::cout << std::endl;
  }

  //--------------------------------------------------------------------------------------
  // construct the transition matrix
  //--------------------------------------------------------------------------------------
  float sigma = 0.1;
  std::vector< std::vector<float> > t_matrix;
  std::vector<float> row_sum;
  bool leap = false;

  // initialize t_matrix size x size
  t_matrix.resize(size);
  for ( int i = 0; i < size; ++i )
    t_matrix[i].resize(size);

  // calculate the sum of each row for t_matrix normalizing
  row_sum.resize(size);
  for ( int i = 0; i < size; ++i ) {
    for ( int j = 0; j < size; ++j ) {
      row_sum[i] = row_sum[i] + link_matrix[i][j];
    }
  }

  std::cout << "t_matrix:" << std::endl;
  for ( int i = 0; i < size; ++i ) {
    for ( int j = 0; j < size; ++j ) {
      if ( leap ) 
        t_matrix[i][j] = sigma / size + (1 - sigma) * link_matrix[i][j] / row_sum[i];
      else
        t_matrix[i][j] = link_matrix[i][j] / row_sum[i];
      std::cout << t_matrix[i][j] << " ";
    }
    std::cout << std::endl;
  }

  //--------------------------------------------------------------------------------------
  // ranking calculation row_vector * t_matrix^N
  //--------------------------------------------------------------------------------------
  
  std::vector<float> row_vector;
  row_vector = t_matrix[0]; 
  
  std::vector<float> rank_vector;
  rank_vector.resize(size);

  float error = 10000;
  float threshold = 0.001;

  std::cout << "ranking calculation" << std::endl;
  for ( int idx = 0; error > threshold ; ++idx ){

    // row_vector * t_matrix
    for ( int j= 0; j < size; ++j ) { 
      float tmp = 0;
      for ( int i = 0; i < size; ++i ) {
        tmp += row_vector[i] * t_matrix[i][j];
      //  std::cout << row_vector[i] << " * " << t_matrix[i][j] << std::endl;
      }
      rank_vector[j] = tmp;
      // std::cout << rank_vector[j] << "\n";
    }


    // error calculation
    error = 0;
    for ( int i = 0; i < size; ++i )
      error += std::abs(rank_vector[i] - row_vector[i]); 
    std::cout << "(" << idx << ")" << " error = " << error;
    std::cout << std::endl;   

 
    row_vector = rank_vector;
  }

  for ( int i = 0; i < size; ++i )
    std::cout << rank_vector[i] << " " << std::endl; 
}

