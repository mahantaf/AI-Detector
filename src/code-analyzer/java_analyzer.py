import javalang

def extract_names_from_expression(expression):
    names = set()
    if isinstance(expression, javalang.tree.BinaryOperation):
        if isinstance(expression.operandl, javalang.tree.MemberReference):
            names.add(expression.operandl.member)
        else:
            names.update(extract_names_from_expression(expression.operandl))
        if isinstance(expression.operandr, javalang.tree.MemberReference):
            names.add(expression.operandr.member)
        else:
            names.update(extract_names_from_expression(expression.operandr))
    elif isinstance(expression, javalang.tree.MemberReference):
        names.add(expression.member)
    elif isinstance(expression, javalang.tree.MethodInvocation):
        names.add(expression.member)
        for argument in expression.arguments:
            names.update(extract_names_from_expression(argument))
    elif isinstance(expression, javalang.tree.Literal):
        pass
    else:
        for child in expression.children:
            if isinstance(child, (javalang.tree.Expression, javalang.tree.BinaryOperation, javalang.tree.MethodInvocation)):
                names.update(extract_names_from_expression(child))
    return names


def extract_operators_from_expression(expression):
    operators = set()
    if isinstance(expression, javalang.tree.BinaryOperation):
        operators.add(expression.operator)
        operators.update(extract_operators_from_expression(expression.operandl))
        operators.update(extract_operators_from_expression(expression.operandr))
    # Simplified handling, focusing on binary operations.
    return operators

def analyze_java_code(java_code):
    tree = javalang.parse.parse(java_code)

    variable_names = set()
    method_names = set()
    method_signatures = {}
    if_else_while_names = set()
    operators = set()
    keywords = set()
    if_else_while_operators = set()

    for _, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            method_names.add(node.name)
            args = [param.name for param in node.parameters]
            method_signatures[node.name] = {"arguments": args, "return_type": node.return_type.name if node.return_type else "void"}
            keywords.add("method")
        elif isinstance(node, javalang.tree.VariableDeclarator):
            variable_names.add(node.name)
            keywords.add("variable")
        elif isinstance(node, (javalang.tree.IfStatement, javalang.tree.WhileStatement)):
            condition_names = extract_names_from_expression(node.condition)
            condition_operators = extract_operators_from_expression(node.condition)
            if_else_while_names.update(condition_names)
            if_else_while_operators.update(condition_operators)
            keywords.add("if" if isinstance(node, javalang.tree.IfStatement) else "while")
        elif isinstance(node, javalang.tree.BinaryOperation):
            operators.add(node.operator)
        # Omitting explicit handling of UnaryOperation due to the AttributeError.

    print("Variable Names:", variable_names)
    print("Method Names:", method_names)
    print("Method Signatures:", method_signatures)
    print("Names in if/else/while statements:", if_else_while_names)
    print("Operators:", operators)
    print("Keywords:", keywords)
    print("Operators in if/else/while statements:", if_else_while_operators)

# Example usage with the provided Java code snippet
java_code = """
public class Test {
    int x = 5;
    boolean b = false;

    public boolean check(int value) {
        if (value > x) {
            return true;
        }
        return false;
    }
    
    public void increment() {
        while (x == 10 || x > 20) {
            x = x + 1;
        }
    }
}
"""

analyze_java_code(java_code)
