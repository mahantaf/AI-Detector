import javalang
from tree_java import ASTNodeJava, SingleNodeJava

def get_sequences(node, sequence):
    if isinstance(node, javalang.tree.Node):
        current = ASTNodeJava(node)
        sequence.append(current.get_token())
        # Correctly access the children as a list, not a callable
        if hasattr(node, 'children'):
            for child in node.children:
                get_sequences(child, sequence)
        # Optionally, mark the end of specific structures, e.g., methods
        if isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
            sequence.append('End')
    elif isinstance(node, list):  # Handling lists of nodes, such as the body of a class or method
        for child in node:
            get_sequences(child, sequence)


# def get_sequences(node, sequence):
#     if isinstance(node, javalang.tree.Node):
#         current = SingleNodeJava(node)
#         sequence.append(current.get_token())
#         for _, child in node.children():
#             get_sequences(child, sequence)
#         # Java doesn't have a direct equivalent to Python's 'End' for functions,
#         # but you might consider marking the end of methods or classes if needed.
#         if isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
#             sequence.append('End')
#     elif isinstance(node, list):  # Handling for nodes that are lists of children
#         for child in node:
#             get_sequences(child, sequence)

def get_blocks(node, block_seq):
    if isinstance(node, javalang.tree.Node):
        # Correctly access the children as a list
        children = list(node.children)
        name = node.__class__.__name__
        
        significant_blocks = [
            javalang.tree.MethodDeclaration, 
            javalang.tree.ConstructorDeclaration, 
            javalang.tree.IfStatement, 
            javalang.tree.ForStatement, 
            javalang.tree.WhileStatement
        ]

        if isinstance(node, tuple(significant_blocks)):
            block_seq.append(ASTNodeJava(node))
            for child in children:
                # Directly iterating over children as a list
                child_name = type(child).__name__ if isinstance(child, javalang.tree.Node) else None
                if child_name and child_name not in ['MethodDeclaration', 'ConstructorDeclaration', 'IfStatement', 'ForStatement', 'WhileStatement', 'BlockStatement']:
                    block_seq.append(ASTNodeJava(child))
                get_blocks(child, block_seq)
            # block_seq.append(ASTNodeJava('End'))  # Marking the end of a block
        elif name == 'BlockStatement':  # Equivalent to 'Compound' in C
            for child in children:
                get_blocks(child, block_seq)
            block_seq.append(ASTNodeJava('End'))
        else:
            for child in children:
                get_blocks(child, block_seq)
    elif isinstance(node, list):  # Handling for nodes that are lists of children
        for child in node:
            get_blocks(child, block_seq)



# def get_blocks(node, block_seq):
#     if isinstance(node, javalang.tree.Node):
#         children = list(node.children)  # Access the children directly as a list
#         name = node.__class__.__name__
        
#         significant_blocks = [
#             'MethodDeclaration', 'ConstructorDeclaration',
#             'IfStatement', 'ForStatement', 'WhileStatement', 'BlockStatement'
#         ]

#         if name in significant_blocks:
#             block_seq.append(ASTNodeJava(node))
#             for child in children:
#                 if isinstance(child, javalang.tree.Node):
#                     get_blocks(child, block_seq)
#             block_seq.append(ASTNodeJava('End'))
#         else:
#             for child in children:
#                 if isinstance(child, javalang.tree.Node):
#                     get_blocks(child, block_seq)
#     elif isinstance(node, list):  # If the node is a list, iterate through its elements
#         for child in node:
#             get_blocks(child, block_seq)


# def get_blocks(node, block_seq):
#     if isinstance(node, javalang.tree.Node):
#         children = list(node.children)
#         name = node.__class__.__name__
        
#         if isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration, javalang.tree.IfStatement, javalang.tree.ForStatement, javalang.tree.WhileStatement)):
#             block_seq.append(ASTNodeJava(node))
#             # Unlike the C version, Java does not use 'skip' logic because
#             # javalang's structure is different, and we iterate through all children directly.
#             for _, child in node.children():
#                 child_name = child.__class__.__name__ if isinstance(child, javalang.tree.Node) else None
#                 if child_name not in ['MethodDeclaration', 'ConstructorDeclaration', 'IfStatement', 'ForStatement', 'WhileStatement', 'BlockStatement']:
#                     block_seq.append(ASTNodeJava(child))
#                 get_blocks(child, block_seq)
#             block_seq.append(ASTNodeJava('End'))  # Marking the end of a block
#         elif name == 'BlockStatement':  # Equivalent to 'Compound' in C
#             for _, child in node.children():
#                 get_blocks(child, block_seq)
#             block_seq.append(ASTNodeJava('End'))
#         else:
#             for _, child in node.children():
#                 get_blocks(child, block_seq)
#     elif isinstance(node, list):  # Handling for nodes that are lists of children
#         for child in node:
#             get_blocks(child, block_seq)
