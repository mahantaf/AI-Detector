import ast

class ASTNodePython(object):
    def __init__(self, node):
        self.node = node
        self.is_str = isinstance(self.node, str)
        self.children = self.add_children()

    def is_leaf(self):
        if self.is_str:
            return True
        # In Python's ast, leaf nodes don't have the 'body' attribute or are instances of ast.Name, ast.Num, etc.
        if isinstance(self.node, (ast.Name, ast.Num, ast.Str, ast.Constant)):
            return True
        return len(self.children) == 0

    def get_token(self, lower=True):
        if self.is_str:
            return self.node
        # Python AST nodes have different types and properties. We need a method to map these to tokens.
        if isinstance(self.node, ast.Name):
            token = self.node.id
        elif isinstance(self.node, ast.Num):
            token = str(self.node.n)
        elif isinstance(self.node, ast.Str):
            token = self.node.s
        elif isinstance(self.node, ast.Constant):  # For Python 3.8+
            token = str(self.node.value)
        else:
            token = self.node.__class__.__name__

        if lower:
            token = token.lower()
        return token
    
    def add_children(self):
        children = []
        if self.is_str:
            return children
        # Python's ast module provides iter_child_nodes for getting children of a node
        for child in ast.iter_child_nodes(self.node):
            children.append(ASTNodePython(child))
        return children

    def children(self):
        return self.children


class SingleNodePython(ASTNodePython):
    def __init__(self, node):
        super().__init__(node)
        # Override the add_children method to ensure SingleNodePython instances have no children
        self.children = []
