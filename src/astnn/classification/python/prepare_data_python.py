import ast
import pandas as pd
import os
import sys
from gensim.models.word2vec import Word2Vec
import pickle
from tree_python import ASTNodePython, SingleNodePython
import numpy as np

import ast

def get_sequence(node, sequence):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        sequence.append(node.__class__.__name__.lower())
        sequence.append(node.name.lower())  # Adding class/function name explicitly
        if hasattr(node, 'decorator_list'):
            for decorator in node.decorator_list:
                sequence.append('@' + decorator.id.lower())

    elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        sequence.append(node.__class__.__name__.lower() + '_start')
        get_sequence(node.elt, sequence)  # Handle the element expression
        for comprehension in node.generators:
            get_sequence(comprehension, sequence)
        sequence.append(node.__class__.__name__.lower() + '_end')
    
    elif isinstance(node, ast.DictComp):
        sequence.append('dictcomp_start')
        get_sequence(node.key, sequence)  # Handle the key expression
        get_sequence(node.value, sequence)  # Handle the value expression
        for comprehension in node.generators:
            get_sequence(comprehension, sequence)
        sequence.append('dictcomp_end')

    elif isinstance(node, ast.Try):
        sequence.append('try_start')
        for body_node in node.body:
            get_sequence(body_node, sequence)
        sequence.append('try_end')
        for handler in node.handlers:
            handler_type = handler.type.id.lower() if handler.type else 'exception'
            sequence.append('except_start ' + handler_type)
            for handler_node in handler.body:
                get_sequence(handler_node, sequence)
            sequence.append('except_end')
        if node.finalbody:
            sequence.append('finally_start')
            for final_node in node.finalbody:
                get_sequence(final_node, sequence)
            sequence.append('finally_end')

    elif isinstance(node, ast.Attribute):
        sequence.append('attribute_access ' + node.attr.lower())
    elif isinstance(node, ast.Call):
        sequence.append('method_call_start')
        get_sequence(node.func, sequence)  # Handle the function being called
        for arg in node.args:
            get_sequence(arg, sequence)  # Handle the arguments to the call
        sequence.append('method_call_end')

    elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        for alias in node.names:
            import_name = alias.name.lower()
            sequence.append('import ' + import_name if isinstance(node, ast.Import) else 'from ' + node.module.lower() + ' import ' + import_name)

    elif hasattr(node, 'id'):  # For variables and function names
        sequence.append(node.id.lower())
    elif isinstance(node, (ast.Num, ast.Str, ast.Constant)):  # For literals
        sequence.append(str(node.value).lower())
    else:  # For other types of nodes, use the class name
        sequence.append(node.__class__.__name__.lower())

    for child in ast.iter_child_nodes(node):
        get_sequence(child, sequence)

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        sequence.append('End')


# def get_sequences(node, sequence):
#     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
#         # Handle both functions and classes, including their names
#         sequence.append(node.__class__.__name__.lower())
#         sequence.append(node.name.lower())  # Adding class/function name explicitly

#     elif hasattr(node, 'id'):
#         sequence.append(node.id.lower())
#     elif isinstance(node, (ast.Num, ast.Str, ast.Constant)):
#         sequence.append(str(node.value).lower())
#     else:
#         sequence.append(node.__class__.__name__.lower())

#     for child in ast.iter_child_nodes(node):
#         get_sequences(child, sequence)

#     # Mark the end of functions/classes definitions
#     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
#         sequence.append('End')


def get_blocks(node, block_seq):
    children = list(ast.iter_child_nodes(node))
    name = type(node).__name__

    if name in ['FunctionDef', 'If', 'For', 'While', 'AsyncFunctionDef', 'ClassDef', 'Try']:
        block_seq.append(ASTNodePython(node))  # Wrap the current node
        if name == 'Try':
            # Process try body
            for try_body_node in node.body:
                get_blocks(try_body_node, block_seq)
            # Process except blocks
            for handler in node.handlers:
                block_seq.append(ASTNodePython(handler))  # Wrap the handler node
                for handler_node in handler.body:
                    get_blocks(handler_node, block_seq)
                block_seq.append('End')  # Optionally, mark the end of each except block
            # Process finally block if it exists
            if node.finalbody:
                block_seq.append(ASTNodePython('finally'))  # Indicate start of finally block
                for final_node in node.finalbody:
                    get_blocks(final_node, block_seq)
                block_seq.append('End')  # Mark the end of finally block
        else:
            for child in children:
                child_name = type(child).__name__
                if child_name not in ['FunctionDef', 'If', 'For', 'While', 'AsyncFunctionDef', 'Module', 'ClassDef', 'Try']:
                    block_seq.append(ASTNodePython(child))
                get_blocks(child, block_seq)
        block_seq.append('End')  # Mark the end of blocks

    elif name == 'Module':
        for child in children:
            get_blocks(child, block_seq)
    else:
        for child in children:
            get_blocks(child, block_seq)

# def get_blocks(node, block_seq):
#     children = list(ast.iter_child_nodes(node))
#     name = type(node).__name__

#     if name in ['FunctionDef', 'If', 'For', 'While', 'AsyncFunctionDef', 'ClassDef']:
#         # Include class definitions in block sequences
#         block_seq.append(ASTNodePython(node))  # Wrap the current node
#         for child in children:
#             child_name = type(child).__name__
#             if child_name not in ['FunctionDef', 'If', 'For', 'While', 'AsyncFunctionDef', 'Module', 'ClassDef']:
#                 block_seq.append(ASTNodePython(child))
#             get_blocks(child, block_seq)
#         block_seq.append('End')  # Mark the end of blocks

#     elif name == 'Module':
#         for child in children:
#             get_blocks(child, block_seq)

#     else:
#         for child in children:
#             get_blocks(child, block_seq)




