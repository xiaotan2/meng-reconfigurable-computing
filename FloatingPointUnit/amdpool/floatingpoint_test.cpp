#include <iostream>
#include <fstream>
#include <string>

#include "floatingpoint.h"


int main()
{
    data_t a = 1.23;
    data_t b = 12.67;
    data_t result = cpp_float(a, b);
    std::cout << "The result is " << result << std::endl;
    return 0;
}
