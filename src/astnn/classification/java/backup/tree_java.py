import javalang

class ASTNodeJava(object):
    def __init__(self, node):
        self.node = node
        self.is_str = isinstance(self.node, str)
        self.children = self.add_children()

    def is_leaf(self):
        # In javalang's AST, leaf nodes usually don't have children
        return len(self.children) == 0
    
    # def get_token(self, lower=True):
        token_parts = []

        # Handling modifiers (public, static, etc.)
        if hasattr(self.node, 'modifiers'):
            token_parts.extend(self.node.modifiers)
        
        # Add the node type name as a string
        token_parts.append(self.node.__class__.__name__)

        # Specific handling for various node types to extract more details
        if isinstance(self.node, javalang.tree.MethodDeclaration):
            token_parts.append(self.node.name)
        elif isinstance(self.node, javalang.tree.FormalParameter):
            token_parts.append(str(self.node.type))  # Ensure conversion to string
            token_parts.append(self.node.name)
        elif isinstance(self.node, javalang.tree.LocalVariableDeclaration):
            for declarator in self.node.declarators:
                token_parts.append(declarator.name)
        elif isinstance(self.node, javalang.tree.VariableDeclarator):
            token_parts.append(self.node.name)
        elif isinstance(self.node, javalang.tree.BinaryOperation):
            token_parts.append(self.node.operator)
        elif isinstance(self.node, javalang.tree.StatementExpression):
            if isinstance(self.node.expression, javalang.tree.Assignment):
                token_parts.append(self.node.expression.expressionl.member)
                token_parts.append(self.node.expression.type)
                if isinstance(self.node.expression.value, javalang.tree.Literal):
                    token_parts.append(str(self.node.expression.value.value))  # Convert Literal to string
                else:
                    token_parts.append(str(self.node.expression.value))  # General case
            elif isinstance(self.node.expression, javalang.tree.MethodInvocation):
                token_parts.append(self.node.expression.member)
                token_parts.append('MethodInvocation')
        
        # Add literal values directly, ensuring they are converted to strings
        if isinstance(self.node, javalang.tree.Literal):
            token_parts.append(str(self.node.value))

        # Optionally, lower all parts for consistency
        if lower:
            token_parts = [str(part).lower() for part in token_parts]  # Ensure everything is a string and then lower it

        # Combine parts into a single token string
        return ' '.join(token_parts)
    
    def get_token(self, lower=True):
        if self.is_str:
            return self.node
        # Mapping node types to tokens, similar to the C and Python versions
        if isinstance(self.node, javalang.tree.MethodDeclaration):
            token = self.node.name
        elif isinstance(self.node, javalang.tree.FieldDeclaration):
            token = 'FieldDeclaration'
        elif isinstance(self.node, javalang.tree.VariableDeclarator):
            token = self.node.name
        elif hasattr(self.node, 'value'):  # For literals
            token = str(self.node.value)
        else:
            token = self.node.__class__.__name__

        if lower:
            token = token.lower()
        return token

    def add_children(self):
        children = []
        if hasattr(self.node, 'children') and callable(getattr(self.node, 'children')):
            # Call .children() if it exists and is callable, then iterate over children
            for _, child_node in self.node.children():
                if isinstance(child_node, javalang.tree.Node):
                    children.append(ASTNodeJava(child_node))
        return children

class SingleNodeJava(ASTNodeJava):
    def __init__(self, node):
        super().__init__(node)
        self.children = []  # No children for single nodes
