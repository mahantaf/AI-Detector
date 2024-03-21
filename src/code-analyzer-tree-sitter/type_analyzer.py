import json
import pandas as pd
# from Levenshtein import ratio

def load_node_types(file_path):
    print(file_path)
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

python_node_types = load_node_types('tree-sitter-python/src/node-types.json')
java_node_types = load_node_types('tree-sitter-java/src/node-types.json')
cpp_node_types = load_node_types('tree-sitter-cpp/src/node-types.json')

def extract_unique_types(data):
    # Extract 'type' values and remove duplicates by converting to a set
    unique_types = list(set(node['type'] for node in data))
    return list(unique_types)

python_types = extract_unique_types(python_node_types)
java_types = extract_unique_types(java_node_types)
cpp_types = extract_unique_types(cpp_node_types)

print("Python Types:", len(python_types))
print("Java Types:", len(java_types))
print("Cpp Types:", len(cpp_types))



import csv
import os
from tree_sitter import Language, Parser

# Assuming the Tree-sitter language grammars are initialized
cpp_parser = Parser()
cpp_parser.set_language(Language('build/my-languages.so', 'cpp'))

java_parser = Parser()
java_parser.set_language(Language('build/my-languages.so', 'java'))

python_parser = Parser()
python_parser.set_language(Language('build/my-languages.so', 'python'))

# Function to extract unique node types from code using a Tree-sitter parser
def extract_unique_node_types(code, parser):
    tree = parser.parse(bytes(code, 'utf8'))
    unique_types = set()

    def traverse(node):
        unique_types.add(node.type)
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)
    return unique_types

# Function to process all CSV files and collect unique node types for each language
def process_datasets(base_dir):
    language_unique_types = {'cpp': set(), 'java': set(), 'python': set()}

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv'):
                lang = root.split('_')[-1]  # Infer language from directory name
                parser = {'cpp': cpp_parser, 'java': java_parser, 'python': python_parser}.get(lang)

                if not parser:
                    continue  # Skip if language parser is not available

                file_path = os.path.join(root, file)
                with open(file_path, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        code = row['code']
                        unique_types = extract_unique_node_types(code, parser)
                        language_unique_types[lang].update(unique_types)

    return language_unique_types

print("Python Types:")
print(python_types)

print()
print("Java Types:")
print(java_types)

print()
print("Cpp Types:")
print(cpp_types)

base_dir = 'data/'
language_unique_types = process_datasets(base_dir)

# Now you have the aggregated unique node types for each language
for lang, types in language_unique_types.items():
    print(f"Unique {lang} types in my dataset:")
    print(types)
    print()
    # print(f"Unique node types in {lang}: {len(types)}")



mapping = {
    'FunctionDeclaration': {
        'python': ['function_definition'],
        'java': ['method_declaration'],
        'cpp': ['function_definition', 'template_method']
    },
    'ClassTypeDeclaration': {
        'python': ['class_definition'],
        'java': ['class_declaration', 'interface_declaration', '@interface'],
        'cpp': ['class_specifier', 'union', 'struct_specifier']
    },
    'LoopConstructs': {
        'python': ['for_statement', 'while_statement'],
        'java': ['for_statement', 'while_statement', 'enhanced_for_statement'],
        'cpp': ['for_statement', 'while_statement', 'for_range_loop']
    },
    'ConditionalConstructs': {
        'python': ['if_statement', 'match_statement'],
        'java': ['if_statement', 'switch_statement'],
        'cpp': ['if_statement', 'switch_statement']
    },
    'TryCatchFinally': {
        'python': ['try', 'except_clause', 'finally_clause'],
        'java': ['try_statement', 'catch_clause', 'finally_clause'],
        'cpp': ['try_statement', 'catch_clause', 'try']
    },
    'ImportInclude': {
        'python': ['import_statement', 'import_from_statement'],
        'java': ['import_declaration'],
        'cpp': ['#include']
    },
    'VariableDeclaration': {
        'python': ['assignment'],
        'java': ['local_variable_declaration'],
        'cpp': ['declaration']
    },
    'BooleanExpressions': {
        'python': ['boolean_operator'],
        'java': ['binary_expression'],
        'cpp': ['binary_expression']
    },
    'FunctionCall': {
        'python': ['call'],
        'java': ['method_invocation'],
        'cpp': ['call_expression']
    },
    'ReturnStatement': {
        'python': ['return_statement'],
        'java': ['return_statement'],
        'cpp': ['return_statement']
    },
    'LiteralExpressions': {
        'python': ['string', 'true', 'false', 'none', 'integer'],
        'java': ['string_literal', 'true', 'false', 'null_literal', 'character_literal', 'decimal_integer_literal'],
        'cpp': ['string_literal', 'true', 'false', 'number_literal', 'char_literal']
    },
    'ArrayDataStructures': {
        'python': ['list', 'tuple'],
        'java': ['array_initializer', 'array_access'],
        'cpp': ['array_declarator', 'subscript_expression']
    },
    # This is a starting point. Further analysis and domain knowledge are required to expand and refine these mappings.
}


mapping = {
    'FunctionDeclaration': {
        'python': ['function_definition'],
        'java': ['method_declaration'],
        'cpp': ['function_definition', 'template_method']
    },
    'ClassTypeDeclaration': {
        'python': ['class_definition'],
        'java': ['class_declaration', 'interface_declaration', '@interface'],
        'cpp': ['class_specifier', 'union', 'struct_specifier']
    },
    'LoopConstructs': {
        'python': ['for_statement', 'while_statement'],
        'java': ['for_statement', 'while_statement', 'enhanced_for_statement'],
        'cpp': ['for_statement', 'while_statement', 'for_range_loop']
    },
    'ConditionalConstructs': {
        'python': ['if_statement', 'match_statement'],
        'java': ['if_statement', 'switch_statement'],
        'cpp': ['if_statement', 'switch_statement']
    },
    'TryCatchFinally': {
        'python': ['try', 'except_clause', 'finally_clause'],
        'java': ['try_statement', 'catch_clause', 'finally_clause'],
        'cpp': ['try_statement', 'catch_clause', 'try']
    },
    'ImportInclude': {
        'python': ['import_statement', 'import_from_statement'],
        'java': ['import_declaration'],
        'cpp': ['#include']
    },
    'VariableDeclaration': {
        'python': ['assignment', 'typed_parameter', 'assignment_expression'],
        'java': ['local_variable_declaration', 'field_declaration'],
        'cpp': ['declaration', 'init_declarator']
    },
    'BooleanExpressions': {
        'python': ['boolean_operator', 'comparison_operator', 'not_operator'],
        'java': ['binary_expression', 'unary_expression'],
        'cpp': ['binary_expression', 'unary_expression']
    },
    'FunctionCall': {
        'python': ['call'],
        'java': ['method_invocation'],
        'cpp': ['call_expression', 'function_declarator']
    },
    'ReturnStatement': {
        'python': ['return_statement'],
        'java': ['return_statement'],
        'cpp': ['return_statement']
    },
    'LiteralExpressions': {
        'python': ['string', 'true', 'false', 'none', 'integer', 'concatenated_string', 'string_content'],
        'java': ['string_literal', 'true', 'false', 'null_literal', 'character_literal', 'decimal_integer_literal', 'hex_integer_literal'],
        'cpp': ['string_literal', 'true', 'false', 'number_literal', 'char_literal', 'raw_string_literal', 'concatenated_string']
    },
    'ArrayDataStructures': {
        'python': ['list', 'tuple'],
        'java': ['array_initializer', 'array_access'],
        'cpp': ['array_declarator', 'subscript_expression', 'array_creation_expression']
    },
    'ErrorHandling': {
        'python': ['raise_statement', 'assert_statement'],
        'java': ['throw_statement', 'assert_statement'],
        'cpp': ['throw_statement', 'static_assert_declaration', 'try_block']
    },
    'Comments': {
        'python': ['comment'],
        'java': ['comment', 'line_comment', 'block_comment'],
        'cpp': ['comment']
    },
    'AnnotationsDecorators': {
        'python': ['decorator'],
        'java': ['annotation'],
        'cpp': ['attribute_specifier']
    },
    'Operators': {
        'python': ['+', '-', '*', '/', '%', '**', '<<', '>>', 'and', 'or', 'not', '&', '|', '^', '~', '<', '>', '==', '!=', '<=', '>=', 'is', 'is not', 'in', 'not in'],
        'java': ['+', '-', '*', '/', '%', '<<', '>>', '&&', '||', '!', '&', '|', '^', '~', '<', '>', '==', '!=', '<=', '>=', 'instanceof'],
        'cpp': ['+', '-', '*', '/', '%', '<<', '>>', '&&', '||', '!', '&', '|', '^', '~', '<', '>', '==', '!=', '<=', '>=', '->', '.*', '::', 'typeid', 'sizeof', 'dynamic_cast', 'static_cast', 'reinterpret_cast', 'const_cast']
    },
    'AssignmentOperators': {
        'python': ['=', '+=', '-=', '*=', '/=', '%=', '**=', '<<=', '>>=', '&=', '|=', '^='],
        'java': ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '|=', '^='],
        'cpp': ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '|=', '^=', '>>>=']
    },
    'ControlFlow': {
        'python': ['if_statement', 'else_clause', 'elif_clause', 'for_statement', 'while_statement', 'break_statement', 'continue_statement'],
        'java': ['if_statement', 'else_statement', 'for_statement', 'while_statement', 'do_statement', 'break_statement', 'continue_statement', 'switch_statement', 'case', 'default'],
        'cpp': ['if', 'else', 'for', 'while', 'do', 'break', 'continue', 'switch', 'case', 'default']
    },
    'DataTypes': {
        'python': ['list', 'tuple', 'dict', 'set', 'int', 'float', 'str', 'bool', 'NoneType'],
        'java': ['int', 'long', 'float', 'double', 'char', 'String', 'boolean', 'byte', 'short', 'List', 'Map', 'Set'],
        'cpp': ['int', 'long', 'float', 'double', 'char', 'bool', 'void', 'auto', 'string', 'vector', 'map', 'set']
    },
    'AccessModifiers': {
        'python': ['public', 'protected', 'private'],  # Python does not enforce access modifiers like Java or C++, but it has naming conventions
        'java': ['public', 'protected', 'private'],
        'cpp': ['public:', 'protected:', 'private:']
    },
    'ObjectOrientedProgramming': {
        'python': ['class_definition', 'method_definition', 'self'],
        'java': ['class_declaration', 'method_declaration', 'this'],
        'cpp': ['class_specifier', 'function_definition', 'this']
    },
    'ErrorHandling': {
        'python': ['try', 'except_clause', 'finally_clause', 'raise'],
        'java': ['try_statement', 'catch_clause', 'finally_clause', 'throw_statement'],
        'cpp': ['try', 'catch', 'throw', 'noexcept']
    },
    'ModulesAndPackages': {
        'python': ['import_statement', 'import_from_statement'],
        'java': ['import_declaration', 'package_declaration'],
        'cpp': ['#include', 'import_declaration', 'module_declaration']
    },
    'Concurrency': {
        'python': ['async_def', 'await', 'async_for', 'async_with'],
        'java': ['synchronized', 'volatile'],
        'cpp': ['thread', 'mutex', 'atomic', 'future', 'async', 'condition_variable']  # C++ concurrency constructs are library-based
    },
        'Literals': {
        'python': ['string', 'integer', 'float', 'true', 'false', 'none', 'bytes', 'formatted_string'],
        'java': ['string_literal', 'decimal_integer_literal', 'hex_integer_literal', 'floating_point_literal', 'true', 'false', 'null_literal', 'character_literal'],
        'cpp': ['string_literal', 'number_literal', 'true', 'false', 'nullptr', 'char_literal', 'floating_point_literal', 'hex_literal', 'binary_literal']
    },
    'Declarations': {
        'python': ['variable_declaration', 'constant_declaration'],  # Python does not have a native constant declaration, but can mimic with naming conventions
        'java': ['local_variable_declaration', 'field_declaration', 'constant_declaration'],
        'cpp': ['declaration', 'field_declaration', 'enumerator', 'namespace_definition']
    },
    'AnnotationsAndMetaData': {
        'python': ['decorator'],
        'java': ['annotation'],
        'cpp': ['attribute_specifier']
    },
    'Visibility': {
        'python': ['public_attribute', 'private_attribute', 'protected_attribute'],  # Using naming conventions (__var, _var)
        'java': ['public', 'private', 'protected'],
        'cpp': ['public:', 'private:', 'protected:']
    },
    'GenericsAndTemplates': {
        'python': ['generic_type', 'type_annotation'],  # Python's type annotations in 3.5+ can serve a similar purpose to generics
        'java': ['generic_type', 'type_parameter', 'type_argument'],
        'cpp': ['template_declaration', 'template_instantiation', 'template_argument']
    },
    'AttributesAndProperties': {
        'python': ['attribute', 'property'],
        'java': ['field_access'],
        'cpp': ['field_identifier', 'field_declaration']
    },
    'Inheritance': {
        'python': ['class_definition'],
        'java': ['class_declaration', 'interface_declaration'],
        'cpp': ['class_specifier', 'struct_specifier']
    },
    'NamespacesAndModules': {
        'python': ['module'],
        'java': ['package_declaration'],
        'cpp': ['namespace_definition']
    },
    'ConstructorsAndInitializers': {
        'python': ['__init__'],
        'java': ['constructor_declaration'],
        'cpp': ['constructor_definition', 'initializer_list']
    },
    'MemoryManagement': {
        'python': [],  # Python's memory management is mostly handled by the interpreter
        'java': [],  # Java's garbage collector handles memory management
        'cpp': ['new_expression', 'delete_expression', 'memory_allocation', 'memory_deallocation']
    },
    'TypeCastingAndConversion': {
        'python': ['cast_expression'],  # Python uses functions like int(), str(), etc. for type conversion
        'java': ['cast_expression'],
        'cpp': ['cast_expression', 'dynamic_cast', 'static_cast', 'reinterpret_cast', 'const_cast']
    },
    'CommentsAndDocumentation': {
        'python': ['comment'],
        'java': ['comment', 'line_comment', 'block_comment', 'javadoc_comment'],
        'cpp': ['comment', 'line_comment', 'block_comment']
    },
}
