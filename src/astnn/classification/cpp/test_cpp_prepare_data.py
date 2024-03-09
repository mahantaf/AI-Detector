import clang.cindex
from prepare_data_cpp import get_sequence, get_blocks  # Assuming these functions are adapted for C++
from tree_cpp import ASTNodeCpp, SingleNodeCpp  # Assuming tree_cpp.py contains these classes


def print_ast(cursor, indentation_level=0):
    """
    Recursively prints the AST nodes.
    :param cursor: The cursor to the node to print.
    :param indentation_level: Current level of indentation for pretty printing.
    """
    if cursor.location.file is not None and cursor.location.file.name.startswith('/usr/include'):
        return
    # Print the current node's kind and spelling (e.g., the name of the variable/function)
    print('  ' * indentation_level + f"{cursor.kind.name} ({cursor.spelling})")
    
    # Recursively print the children nodes
    for child in cursor.get_children():
        print_ast(child, indentation_level + 1)

def test_cpp_code(cpp_code_str):
    # Initialize Clang index
    index = clang.cindex.Index.create()
    # Parse the C++ code string into an AST
    tu = index.parse('test.cpp', args=['-std=c++14'], unsaved_files=[('test.cpp', cpp_code_str)],  options=0)
    
    print_ast(tu.cursor)

    # print()

    # sequences = []
    # get_sequence(tu.cursor, sequences)
    # print("C++ Sequences:", sequences)
    # print()
    # blocks = []
    # get_blocks(tu.cursor, blocks)
    # print("C++ Blocks:", blocks)

if __name__ == "__main__":
    cpp_code = """
#include<stdio.h>
#include<vector>
#include<string>
using namespace std;
#include<algorithm>
#include<math.h>
#include<stdlib.h>
vector<string> filter_by_substring(vector<string> strings, string substring){
    vector<string> out;

    for (int i=0;i<strings.size();i++)
    {
        if (strings[i].find(substring)!=strings[i].npos)
            out.push_back(strings[i]);
    }
    return out;
}
"""
    test_cpp_code(cpp_code)
