#include <vector>

vector<vector<int>> toLinkMatrix(vector<vector<int>> inMap) {
  int n = inMap.size();
  vector<vector<int>> result(n, vector<int> (n,0));

  // construct an array to find out outgoing edges of each node
  vector<int> outEdges(n, 0);

  // firstly, find the information on outgoing edges
  for(int i = 0; i < n; ++i) {
    int count = 0;
    for(int j = 0; j < n; ++j) {
      if(inMap[i][j] == 1)
        ++count;
    }
    outEdges[i] = count;
  }

  // Then, use outEdges information to build matrix
  for(int i = 0; i < n; ++i) {
    for(int j = 0; j < n; ++j) {
      if(inMap[j][i] == 1)
        result[i][j] = 1/outEdges[j];
    }
  }

  return result;

}
