from tree_sitter import Language, Parser
import string


def rename_variables(tree, code):
    var_counter = 1
    variable_mappings = {}  # Map original variable names to their new names

    def collect_variables(node):
        nonlocal var_counter

        if node.type == 'identifier' and code[node.start_byte:node.end_byte] == 'self':
            return
        

        if node.type == 'pattern_list':
            for c in node.children:
                if c.type == 'identifier':
                    original_name = code[c.start_byte:c.end_byte]
                    if original_name not in variable_mappings:
                        new_name = f"var_{var_counter}"
                        variable_mappings[original_name] = new_name
                        var_counter += 1

        if node.type == 'function_definition':
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for param in params_node.children:
                    if param.type == 'typed_parameter':
                        for tp in param.children:
                            if tp.type == 'identifier':
                                original_name = code[tp.start_byte:tp.end_byte]
                                if original_name not in variable_mappings:
                                    new_name = f"var_{var_counter}"
                                    variable_mappings[original_name] = new_name
                                    var_counter += 1
                            
                    if param.type == 'identifier':
                        original_name = code[param.start_byte:param.end_byte]
                        if original_name == 'self':
                            continue
                        if original_name not in variable_mappings:
                            new_name = f"var_{var_counter}"
                            variable_mappings[original_name] = new_name
                            var_counter += 1

        if node.type == 'assignment':
            # Extract variable name from the left-hand side of the assignment
            target_node = node.children[0]
            if target_node.type == 'identifier':
                original_name = code[target_node.start_byte:target_node.end_byte]
                if original_name == 'self':
                    return
                if original_name not in variable_mappings:
                    new_name = f"var_{var_counter}"
                    variable_mappings[original_name] = new_name
                    var_counter += 1
        
        # Check for variables used in for loops
        elif node.type == 'for_statement':
            for child in node.children:
                if child.type == 'identifier':
                    original_name = code[child.start_byte:child.end_byte]
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
                # Before replacement, calculate any offset caused by previous replacements
                offset = len(modified_code) - len(code)
                # Adjust start and end positions considering the offset
                adjusted_start = node.start_byte + offset
                adjusted_end = node.end_byte + offset
                # Replace the original name with the new name in the modified_code
                modified_code = modified_code[:adjusted_start] + new_name + modified_code[adjusted_end:]
        for child in node.children:
            modified_code = apply_renaming(child, modified_code)
        return modified_code
    
    # print(variable_mappings)
    modified_code = apply_renaming(tree.root_node, code)
    return modified_code

def replace_function_names(tree, code):
    function_names = []
    counter = 1  # Start numbering from 1

    def collect_function_names(node):
        if node.type == 'function_definition':
            function_name_node = node.child_by_field_name('name')
            if function_name_node:
                function_name = code[function_name_node.start_byte:function_name_node.end_byte]
                # Skip renaming __init__ methods
                if function_name != '__init__':
                    function_names.append(function_name)
        for child in node.children:
            collect_function_names(child)

    collect_function_names(tree.root_node)

    # Generate mappings, excluding __init__
    name_mappings = {name: f"func_{i+1}" for i, name in enumerate(function_names)}

    # Replacing function names and their calls in the source code, except __init__
    new_code = code
    for original_name, mapped_name in name_mappings.items():
        new_code = new_code.replace(original_name, mapped_name)

    return new_code

def remove_comments(tree, code):
    comment_ranges = []

    def collect_comment_ranges(node):
        if node.type == 'comment':
            comment_ranges.append((node.start_byte, node.end_byte))
        for child in node.children:
            collect_comment_ranges(child)

    collect_comment_ranges(tree.root_node)

    # Now, create a new version of the code without the comment ranges
    new_code = ""
    last_end = 0
    for start, end in sorted(comment_ranges):
        new_code += code[last_end:start]
        last_end = end
    new_code += code[last_end:]

    return new_code

def get_node_text(node, code):
    """
    Get the text that a node corresponds to in the source code.
    """
    start_byte = node.start_byte
    end_byte = node.end_byte
    return code[start_byte:end_byte]

def F(node, code):
    """
    Map an AST node to a sequence of tokens including actual code tokens.
    """
    seq = []
    name = node.type
    text = get_node_text(node, code).decode('utf8')  # Assuming code is a bytes object

    if len(node.children) == 0 or node.type == 'identifier':  # Check if the node is a leaf or an identifier
        seq.append(text)
    else:
        seq.append(f"{name}::left")
        for child in node.children:
            seq.extend(F(child, code))  # Recursive call
        seq.append(f"{name}::right")

    return seq