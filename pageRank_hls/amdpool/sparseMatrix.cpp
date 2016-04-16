//=========================================================================
// sparseMatrix.cpp
//=========================================================================
// @brief : A program calculates the transition matrix for a graph in adjacency list format.

#include "sparseMatrix.h"

#include <cmath>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <iterator>

#define P_VALUE 0.15

using namespace std;

vector<float> sparseMatrixMul(vector<float> A, vector<int> IA, vector<int> JA, vector<float> R) {
  // calculate sparse matrix multiplication between a sparse matrix and a vector result
  vector<float> result (R.size(), 0);
  for(int i = 0; i < result.size(); ++i) {
    for(int k = IA[i]; k < IA[i+1]; ++k) {
      result[i] = result[i] + A[k] * R[JA[k]];
      result[i] *= (1-P_VALUE);
    }
  }
  return result;
}

vector<float> vectorMul(vector<float> V, float value) {
  vector<float> result(V.size(), 0);
  for(int i = 0; i < V.size(); ++i) {
    result[i] = V[i]*value;
  }
  return result;
}

vector<float> vectorAdd(vector<float> V1, vector<float> V2) {
  vector<float> result(V1.size(), 0);
  for(int i = 0; i < V1.size(); ++i) {
    result[i] = V1[i] + V2[i];
  }
  return result;
}

int main()
{
  // Read input file of the graph in adjacency list format
  string line;
  ifstream myfile("data/graph2.dat");

  //--------------------------------------------------------------------------------------
  // construct the link matrix
  //--------------------------------------------------------------------------------------

  int nodes;
  int edges;
  vector<vector<int> > link_matrix;
  vector<float> A;
  vector<int> IA;
  IA.push_back(0);
  vector<int> JA;
  vector<int> node_sum;

  if ( myfile.is_open() ){

    // read first line, get total number of nodes in the graph
    getline( myfile, line ); 
    stringstream stream1( line );
    stream1 >> nodes;
    cout << "node size = " << nodes << "\n";

    vector<vector<int> > matrix (nodes, vector<int>(nodes));
    vector<int> sum (nodes, 0);

    getline( myfile, line);
    stringstream stream2(line);
    stream2 >> edges;
    cout << "edge size = " << edges << "\n";

    int row = 0;
    while ( getline( myfile, line ) ){
      stringstream stream( line );

      vector<int> values( (istream_iterator<int>(stream)), (istream_iterator<int>()) );

      vector<int>::iterator value = values.begin();
      // source
      int source = *value;
      ++value;
      // destination
      int dest = *value;
      ++value;
      // weight
      int weight = *value;
      ++value;
      matrix[source][dest] = weight;
      sum[source] += weight;
    }
    link_matrix = matrix;
    node_sum = sum;
  }
  else {
    std::cout << "Unable to open the file";
  }

  cout << "link_matrix:" << endl;
  for ( int i = 0; i < nodes; ++i ) {
    for ( int j = 0; j < nodes; ++j ) {
      cout << link_matrix[i][j] << " ";
    }
    cout << endl;
  }

  //--------------------------------------------------------------------------------------
  // construct the sparse matrix
  //--------------------------------------------------------------------------------------

  for(int i = 0; i < link_matrix[0].size(); ++i) {
    int count = 0;
    for(int j = 0; j < link_matrix.size(); ++j) {
      if(link_matrix[j][i] != 0) {
        A.push_back(((float)link_matrix[j][i])/((float)node_sum[j]));
        ++count;
        JA.push_back(j);
      }
    }
    IA.push_back(count + IA[i]);
  }

  cout << "A:" << endl;
  for(int i = 0; i < A.size(); ++i) {
    cout << A[i] << " ";
  }
  cout << endl;

  cout << "IA:" << endl;
  for(int i = 0; i < IA.size(); ++i) {
    cout << IA[i] << " ";
  }
  cout << endl;
  
  cout << "JA:" << endl;
  for(int i = 0; i < JA.size(); ++i) {
    cout << JA[i] << " ";
  }
  cout << endl;
  //--------------------------------------------------------------------------------------
  // ranking calculation row_vector * t_matrix^N
  //--------------------------------------------------------------------------------------
  
  vector<float> row_vector (nodes, (1/(float)nodes));
  
  vector<float> rank_vector (nodes, 0);

  float error = 10000;
  float threshold = 0.001;

  cout << "ranking calculation" << std::endl;
  for ( int idx = 0; error > threshold ; ++idx ){

    vector<float> vector1 = sparseMatrixMul(A, IA, JA, row_vector);
    vector<float> vector2 = vectorMul(row_vector, (P_VALUE/(float)nodes));
    rank_vector = vectorAdd(vector1, vector2);

  //  cout << "vector1:" << endl;
  //  for(int i = 0; i < vector1.size(); ++i) {
  //    cout << vector1[i] << " ";
  //  }
  //  cout << endl;
    
  //  cout << "vector2:" << endl;
  //  for(int i = 0; i < vector2.size(); ++i) {
  //    cout << vector2[i] << " ";
  //  }
  //  cout << endl;
    
    cout << "rank vector:" << endl;
    for(int i = 0; i < rank_vector.size(); ++i) {
      cout << rank_vector[i] << " ";
    }
    cout << endl;

    // error calculation
    error = 0;
    for ( int i = 0; i < nodes; ++i )
      error += abs(rank_vector[i] - row_vector[i]); 
    cout << "(" << idx << ")" << " error = " << error;
    cout << endl;   

 
    row_vector = rank_vector;
  }

  for ( int i = 0; i < nodes; ++i )
    cout << rank_vector[i] << " " << endl; 
}

