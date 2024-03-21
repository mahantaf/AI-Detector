from tree_sitter import Language, Parser

# Load the language grammars (adjust paths as necessary)
Language.build_library(
  # Store the library in the current directory
  'build/my-languages.so',
  [
    'tree-sitter-python',
    'tree-sitter-java',
    'tree-sitter-cpp'
  ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')

# Create a new parser instance
parser = Parser()

# For Python
parser.set_language(PY_LANGUAGE)
tree = parser.parse(bytes('def foo(): pass', "utf8"))

# For Java, set_language to JAVA_LANGUAGE and parse Java code
# For C++, set_language to CPP_LANGUAGE and parse C++ code

# Traverse the tree
root_node = tree.root_node
print('Root node type:', root_node.type)

# You can then traverse the AST as needed, for example:
for child in root_node.children:
    print('Child node type:', child.type, 'with text:', child.text)
