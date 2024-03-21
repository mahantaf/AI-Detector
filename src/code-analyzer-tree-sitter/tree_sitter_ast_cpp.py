from tree_sitter import Language, Parser
import string

def rename_variables(tree, code):
    var_counter = 1
    variable_mappings = {}

    def collect_variables(node):
        nonlocal var_counter
        # Handle C++ variable declarations including simple variables, pointers, and references
        if node.type in ['declaration', 'init_declarator', 'parameter_declaration', 'structured_binding_declarator']:
            for child in node.children:
                # if child.type in ['identifier', 'type_identifier', 'field_identifier']:
                if child.type == 'identifier':
                    identifier = child
                    original_name = code[identifier.start_byte:identifier.end_byte]
                    if original_name not in variable_mappings:
                        new_name = f"var_{var_counter}"
                        variable_mappings[original_name] = new_name
                        var_counter += 1
        
        for child in node.children:
            collect_variables(child)

    collect_variables(tree.root_node)

    def apply_renaming(node, modified_code):
        if node.type == 'identifier':
            original_name = code[node.start_byte:node.end_byte]
            if original_name in variable_mappings:
                new_name = variable_mappings[original_name]
                offset = len(modified_code) - len(code)
                adjusted_start = node.start_byte + offset
                adjusted_end = node.end_byte + offset
                modified_code = modified_code[:adjusted_start] + new_name + modified_code[adjusted_end:]
        for child in node.children:
            modified_code = apply_renaming(child, modified_code)
        return modified_code
    modified_code = code
    modified_code = apply_renaming(tree.root_node, modified_code)
    return modified_code

def get_node_text(node, code):
    start_byte = node.start_byte
    end_byte = node.end_byte
    return code[start_byte:end_byte]

def remove_comments(tree, code):
    comment_ranges = []

    def collect_comment_ranges(node):
        # In C++, comments are of type 'comment'
        if node.type in ['comment']:
            comment_ranges.append((node.start_byte, node.end_byte))
        for child in node.children:
            collect_comment_ranges(child)
            
    collect_comment_ranges(tree.root_node)

    new_code = ""
    last_end = 0
    for start, end in sorted(comment_ranges):
        new_code += code[last_end:start]  # Directly work with string slice
        last_end = end
    new_code += code[last_end:]  # Ensure the remaining code is added

    return new_code

def replace_function_names(tree, code):
    replacements = {}
    counter = 1

    def collect_function_names(node, is_global_scope=True, class_name=None):
        nonlocal counter

        if node.type == 'class_specifier':
            class_name_node = node.child_by_field_name('name')
            if class_name_node:
                class_name = code[class_name_node.start_byte:class_name_node.end_byte]
            # Indicate that we are now inside a class
            is_global_scope = False

        if node.type == 'function_definition':
            function_declrator_node = next((child for child in node.children if child.type == 'function_declarator'), None)
            
            identifier_node = next((child for child in function_declrator_node.children if child.type in ['identifier', 'destructor_name', 'field_identifier']), None)
            if identifier_node:
                function_name = code[identifier_node.start_byte:identifier_node.end_byte]
                if function_name != 'main' and (is_global_scope or function_name not in [class_name, f'~{class_name}']):
                    # Generate new function name and map it
                    new_function_name = f'func_{counter}'
                    replacements[function_name] = new_function_name
                    counter += 1
        # Recurse into children nodes
        for child in node.children:
            collect_function_names(child, is_global_scope, class_name)

    collect_function_names(tree.root_node)

    # Apply the replacements
    new_code = code
    for original, replacement in replacements.items():
        new_code = new_code.replace(f"{original}(", f"{replacement}(")

    return new_code

def F(node, code):
    seq = []
    name = node.type
    text = get_node_text(node, code).decode('utf8')

    # Include identifiers and other literals directly
    if len(node.children) == 0 or node.type in ['identifier', 'string_literal', 'number_literal', 'char_literal', 'preproc_include', 'system_lib_string']:
        seq.append(text)
    else:
        seq.append(f"{name}::left")
        for child in node.children:
            seq.extend(F(child, code))
        seq.append(f"{name}::right")

    return seq

def analyze_cpp_code(tree, code):
    total_tokens = 0
    unique_keywords = set()
    unique_operators = set()
    cpp_keywords = [
        "alignas", "alignof", "and", "and_eq", "asm", "atomic_cancel", "atomic_commit",
        "atomic_noexcept", "auto", "bitand", "bitor", "bool", "break", "case", "catch",
        "char", "char8_t", "char16_t", "char32_t", "class", "compl", "concept", "const",
        "consteval", "constexpr", "constinit", "const_cast", "continue", "co_await",
        "co_return", "co_yield", "decltype", "default", "delete", "do", "double",
        "dynamic_cast", "else", "enum", "explicit", "export", "extern", "false", "float",
        "for", "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace",
        "new", "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private",
        "protected", "public", "reflexpr", "register", "reinterpret_cast", "requires",
        "return", "short", "signed", "sizeof", "static", "static_assert", "static_cast",
        "struct", "switch", "synchronized", "template", "this", "thread_local", "throw",
        "true", "try", "typedef", "typeid", "typename", "union", "unsigned", "using",
        "virtual", "void", "volatile", "wchar_t", "while", "xor", "xor_eq"
    ]
    cpp_operators = ['&&', '||', '!', '<', '>', '<=', '>=', '==', '!=', '|', '&']

    def extract_type_from_declaration(node):
        if "primitive_type" in node.type:
            for child in node.children:
                if child.type == "type_identifier" or child.type in cpp_keywords:
                    type_name = code[child.start_byte:child.end_byte]
                    unique_keywords.add(type_name)

    def traverse(node):
        nonlocal total_tokens

        # Increment token count for leaf nodes
        if len(node.children) == 0:
            total_tokens += 1
        
        if "primitive_type" in node.type:
            unique_keywords.add(get_node_text(node, code))
        
        # extract_type_from_declaration(node)
        
        if node.type in cpp_keywords:
            unique_keywords.add(node.type)

        # Specifically handle the condition part of control flow statements
        if node.type in ['if_statement', 'while_statement', 'for_statement']:
            condition = None
            if node.type == 'if_statement' or node.type == 'while_statement':
                condition = node.child_by_field_name('condition')
            elif node.type == 'for_statement':
                condition = node.child_by_field_name('condition')
            if condition:
                extract_operators(condition)

        # General traversal for other nodes
        for child in node.children:
            traverse(child)

    # Function to extract operators from a condition node
    def extract_operators(node):
        if node.type == 'binary_expression' and any(op in code[node.start_byte:node.end_byte] for op in cpp_operators):
            operator_text = code[node.start_byte:node.end_byte]
            for op in cpp_operators:
                if op in operator_text:
                    unique_operators.add(op)
        for child in node.children:
            extract_operators(child)

    traverse(tree.root_node)
    return len(unique_keywords)/total_tokens, len(unique_operators)/total_tokens