import clang.cindex
from clang.cindex import CursorKind, TokenKind

class CppCodeAnalyzer:
    def __init__(self):
        # clang.cindex.Config.set_library_file('/path/to/your/libclang.so')  # Adjust this path
        self.index = clang.cindex.Index.create()
        self.variables = set()
        self.functions = set()
        self.signatures = {}
        self.operators = set()
        self.keywords = {'if', 'else', 'while'}
        self.if_else_while_operators = set()
        self.if_else_while_names = set()

    def analyze(self, code):
        tu = self.index.parse('tmp.cpp', args=['-std=c++14'], unsaved_files=[('tmp.cpp', code)], options=0)
        self.visit(tu.cursor)

    def visit(self, node):
        if node.kind == CursorKind.VAR_DECL or node.kind == CursorKind.PARM_DECL:
            self.variables.add(node.spelling)
        elif node.kind == CursorKind.FUNCTION_DECL:
            self.functions.add(node.spelling)
            self.signatures[node.spelling] = {
                'arguments': [arg.spelling for arg in node.get_arguments()],
                'return_type': node.result_type.spelling
            }
        elif node.kind in [CursorKind.BINARY_OPERATOR, CursorKind.UNARY_OPERATOR, CursorKind.COMPOUND_ASSIGNMENT_OPERATOR]:
            # Extract operator tokens directly from the node's tokens
            for token in node.get_tokens():
                if token.kind == TokenKind.PUNCTUATION:
                    self.operators.add(token.spelling)
                    if self.is_within_control_flow(node):
                        self.if_else_while_operators.add(token.spelling)
        elif node.kind in [CursorKind.IF_STMT, CursorKind.WHILE_STMT]:
            self.extract_condition_details(node)

        for c in node.get_children():
            self.visit(c)

    def is_within_control_flow(self, node):
        while node:
            if node.kind in [CursorKind.IF_STMT, CursorKind.WHILE_STMT]:
                return True
            node = node.semantic_parent
        return False

    def extract_condition_details(self, node):
        # For `if` and `while`, the condition is typically the first child.
        for child in node.get_children():
            if child.kind == CursorKind.BINARY_OPERATOR or child.kind == CursorKind.UNARY_OPERATOR or child.kind == CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
                self.if_else_while_operators.update([token.spelling for token in child.get_tokens() if token.kind == TokenKind.PUNCTUATION])
            if child.kind == CursorKind.DECL_REF_EXPR:
                self.if_else_while_names.add(child.spelling)
            # Recursively check for variables and operators within the condition
            self.extract_condition_details(child)

    def report(self):
        print("Variables:", self.variables)
        print("Functions:", self.functions)
        print("Function Signatures:", self.signatures)
        print("Operators:", self.operators)
        print("Keywords:", self.keywords)
        print("If/Else/While Operators:", self.if_else_while_operators)
        print("If/Else/While Variable Names:", self.if_else_while_names)

# Example usage
code = """
#include <iostream>
using namespace std;

int add(int x, int y) {
    return x + y;
}

int main() {
    int result = add(5, 3);
    int b = 10;
    if (result > 0 || b == 10) {
        cout << "Positive";
    }
    return 0;
}
"""

analyzer = CppCodeAnalyzer()
analyzer.analyze(code)
analyzer.report()
