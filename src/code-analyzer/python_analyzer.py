import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()
        self.functions = set()
        self.signatures = {}
        self.operators = set()
        self.keywords = set()
        self.if_else_while_names = set()
        self.if_else_while_operators = set()
        # Mapping of AST operator class names to their symbols
        self.operator_symbols = {
            'Add': '+',
            'Sub': '-',
            'Mult': '*',
            'Div': '/',
            'Mod': '%',
            'Pow': '**',
            'LShift': '<<',
            'RShift': '>>',
            'BitOr': '|',
            'BitXor': '^',
            'BitAnd': '&',
            'FloorDiv': '//',
            'Gt': '>',
            'Lt': '<',
            'GtE': '>=',
            'LtE': '<=',
            'Eq': '==',
            'NotEq': '!=',
            'And': 'and',
            'Or': 'or',
            'Not': 'not',
            'In': 'in',
            'NotIn': 'not in',
            'Is': 'is',
            'IsNot': 'is not',
        }

    def visit_Name(self, node):
        self.variables.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        args = [arg.arg for arg in node.args.args]

        self.signatures[node.name] = {"arguments": args, "return_type": []}
        if hasattr(node, 'returns') and node.returns is not None:
            self.signatures[node.name]["return_type"].append(ast.unparse(node.returns))
        else:
            self.signatures[node.name]["return_type"].append('None')
        self.generic_visit(node)
    
    def visit_BinOp(self, node):
        operator_symbol = self.operator_symbols[type(node.op).__name__]
        self.operators.add(operator_symbol)
        self.generic_visit(node)

    def visit_Compare(self, node):
        for op in node.ops:
            operator_symbol = self.operator_symbols[type(op).__name__]
            self.operators.add(operator_symbol)
        self.generic_visit(node)

    def visit_If(self, node):
        self.keywords.add('if')
        self._process_conditional(node.test)
        self.generic_visit(node)

    def visit_While(self, node):
        self.keywords.add('while')
        self._process_conditional(node.test)
        self.generic_visit(node)

    def _process_conditional(self, test):
        if isinstance(test, ast.Name):
            self.if_else_while_names.add(test.id)
        elif isinstance(test, (ast.BinOp, ast.Compare)):
            for name in ast.walk(test):
                if isinstance(name, ast.Name):
                    self.if_else_while_names.add(name.id)
            if hasattr(test, 'op'):
                self.if_else_while_operators.add(self.operator_symbols[type(test.op).__name__])
            else:
                for op in test.ops:
                    self.if_else_while_operators.add(self.operator_symbols[type(op).__name__])

    def report(self):
        print("Variables:", self.variables)
        print("Functions:", self.functions)
        print("Function Signatures:", self.signatures)
        print("Operators:", self.operators)
        print("Keywords:", self.keywords)
        print("Names in if/else/while:", self.if_else_while_names)
        print("Operators in if/else/while:", self.if_else_while_operators)

def analyze_code(code):
    tree = ast.parse(code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    analyzer.report()

# Example Usage:
code = """
def foo(x):
    if x > 10:
        return True
    else:
        y = x + 2
        return False

while x == 10:
    x += 1
"""

analyze_code(code)
