//=========================================================================
// sparseMatrix.cpp
//=========================================================================
// @brief : A program calculates the transition matrix for a graph in adjacency list format.

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

  myfile.close();
  
  //--------------------------------------------------------------------------------------
  // Print .h
  //--------------------------------------------------------------------------------------

  ofstream wfile;
  wfile.open ("test-cl.h");

  wfile << "#define MATRIX_RANK " << nodes << endl << endl;

  wfile << "#define A_SIZE " << A.size() << endl;

  wfile << "#define IA_SIZE " << IA.size() << endl;
  
  wfile << "#define JA_SIZE " << JA.size() << endl;
  
  wfile << "float A[" << A.size() << "] = { ";
  for(int i = 0; i < A.size(); ++i) {
    if ( i == A.size()-1 )
      wfile << A[i] << " };" << endl;
    else 
      wfile << A[i] << ", ";
  }
  wfile << endl;

  wfile << "int IA[" << IA.size() << "] = { ";
  for(int i = 0; i < IA.size(); ++i) {
    if ( i == IA.size()-1 )
      wfile << IA[i] << " };" << endl;
    else 
      wfile << IA[i] << ", ";
  }
  wfile << endl;
 
  wfile << "int JA[" << JA.size() << "] = { ";
  for(int i = 0; i < JA.size(); ++i) {
    if ( i == JA.size()-1 )
      wfile << JA[i] << " };" << endl;
    else 
      wfile << JA[i] << ", ";
  }
  wfile << endl;

  wfile.close();

}
