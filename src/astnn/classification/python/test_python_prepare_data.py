# Assuming prepare_data.py for Python has been adapted as described and saved as prepare_data_python.py
import ast
from prepare_data_python import get_sequence, get_blocks
from tree_python import ASTNodePython

def test_python_code():
    python_code = """
from typing import List

def filter_by_substring(strings: List[str], substring: str) -> List[str]:
    return [x for x in strings if substring in x]

"""

    ast_tree = ast.parse(python_code)
    sequences = []
    get_sequence(ast_tree, sequences)
    print("Python Sequences:", sequences)

    print()

    blocks = []
    get_blocks(ast_tree, blocks)

    print("Python Blocks:")
    new_blocks = []
    for block in blocks:
        if isinstance(block, ASTNodePython):  # Check if the item is an ASTNodePython instance
            new_blocks.append(block.get_token())
        else:  # This handles string items, such as 'End'
            new_blocks.append(block)
    print(new_blocks)


test_python_code()
