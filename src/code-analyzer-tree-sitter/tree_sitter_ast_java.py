from tree_sitter import Language, Parser
import string

def rename_variables(tree, code):
    var_counter = 1
    variable_mappings = {}

    def collect_variables(node):
        nonlocal var_counter
        # Handle different types of variable declarations in Java
        # print(node.type)

        if node.type == 'catch_formal_parameter':
            for child in node.children:
                if child.type == 'identifier':
                    original_name = code[child.start_byte:child.end_byte]
                    if original_name not in variable_mappings:
                            new_name = f"var_{var_counter}"
                            variable_mappings[original_name] = new_name
                            var_counter += 1

        if node.type == 'enhanced_for_statement':
            for child in node.children:
                if child.type == 'identifier':
                    original_name = code[child.start_byte:child.end_byte]
                    if original_name not in variable_mappings:
                            new_name = f"var_{var_counter}"
                            variable_mappings[original_name] = new_name
                            var_counter += 1
                

        if node.type in ['local_variable_declaration', 'formal_parameter', 'field_declaration']:
            for child in node.children:
                if child.type == 'identifier':
                    original_name = code[child.start_byte:child.end_byte]
                    if original_name not in variable_mappings:
                            new_name = f"var_{var_counter}"
                            variable_mappings[original_name] = new_name
                            var_counter += 1

                # Java variable declarations can include modifiers; we want the actual variable names
                if child.type == 'variable_declarator':
                    identifier = child.child_by_field_name('name')
                    if identifier is not None:
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

    # print(variable_mappings)
    modified_code = code
    modified_code = apply_renaming(tree.root_node, modified_code)
    return modified_code

def replace_method_names(tree, code):
    method_mappings = {}
    counter = 1  # Start numbering from 1

    def collect_method_names(node, has_override=False):
        nonlocal counter
        # Check if current node or any of its siblings (if it's an annotation) is @Override
        # if node.type == 'annotation' and code[node.start_byte:node.end_byte] == '@Override':
        #     has_override = True

        if node.type == 'method_declaration':
            method_name_node = node.child_by_field_name('name')
            if method_name_node:
                method_name = code[method_name_node.start_byte:method_name_node.end_byte]
                # Skip renaming if the method is main or has an @Override annotation
                if method_name != 'main' and not has_override:
                    new_method_name = f"func_{counter}"
                    method_mappings[method_name] = new_method_name
                    counter += 1
        
        # Pass has_override flag to children to remember if @Override was seen
        for child in node.children:
            collect_method_names(child, has_override)

    collect_method_names(tree.root_node)

    # Replacing method names in the source code
    new_code = code
    for original_name, new_name in method_mappings.items():
        # Ensuring that method invocations are accurately targeted
        new_code = new_code.replace(f" {original_name}(", f" {new_name}(")

    return new_code

def get_node_text(node, code):
    start_byte = node.start_byte
    end_byte = node.end_byte
    return code[start_byte:end_byte]

def remove_comments(tree, code):
    comment_ranges = []

    def collect_comment_ranges(node):
        # In Java, comments can be of type 'comment', 'line_comment', or 'block_comment'
        if node.type in ['comment', 'line_comment', 'block_comment']:
            comment_ranges.append((node.start_byte, node.end_byte))
        for child in node.children:
            collect_comment_ranges(child)
            
    collect_comment_ranges(tree.root_node)

    # Create a new version of the code without the comment ranges
    new_code = ""
    last_end = 0
    for start, end in sorted(comment_ranges):
        new_code += code[last_end:start]  # Directly work with string slice
        last_end = end
    new_code += code[last_end:]  # Ensure the remaining code is added

    return new_code

def F(node, code):
    seq = []
    name = node.type
    text = get_node_text(node, code).decode('utf8')

    # Include identifiers and other literals directly
    if len(node.children) == 0 or node.type in ['identifier', 'string_literal', 'number_literal']:
        seq.append(text)
    else:
        seq.append(f"{name}::left")
        for child in node.children:
            seq.extend(F(child, code))
        seq.append(f"{name}::right")

    return seq

def analyze_java_code(tree, code):
    total_tokens = 0
    unique_keywords = set()
    unique_operators = set()
    
    # Define Java keywords, including primitive types and control structures
    java_keywords = [
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
        "continue", "default", "do", "double", "else", "enum", "exports", "extends", "final", "finally",
        "float", "for", "if", "implements", "import", "instanceof", "int", "interface", "long", "module",
        "native", "new", "package", "private", "protected", "public", "requires", "return", "short", "static",
        "strictfp", "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "var",
        "void", "volatile", "while", "true", "false", "null"
    ]
    
    # Define operators used in conditional statements
    java_operators = ['&&', '||', '!', '<', '>', '<=', '>=', '==', '!=']

    def traverse(node, within_condition=False):
        nonlocal total_tokens
        
        # Increment token count for leaf nodes
        if len(node.children) == 0:
            total_tokens += 1
            
        node_text = get_node_text(node, code)
        
        # Add keywords
        if node.type in java_keywords:
            unique_keywords.add(node_text)

        # Check for operators within conditions
        if within_condition and node_text in java_operators:
            unique_operators.add(node_text)

        # Adjust traversal to check for conditions in if, for, and while statements
        new_within_condition = within_condition or node.type in ['if_statement', 'for_statement', 'while_statement']
        
        for child in node.children:
            traverse(child, new_within_condition)
            
    traverse(tree.root_node)
    return len(unique_keywords)/total_tokens, len(unique_operators)/total_tokens