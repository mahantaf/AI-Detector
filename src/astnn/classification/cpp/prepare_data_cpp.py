import clang.cindex
from clang.cindex import CursorKind

from tree_cpp import ASTNodeCpp, SingleNodeCpp

def get_operator_symbol(cursor):
    """
    Extracts the operator symbol from the cursor's tokens.
    """
    # This handles binary and unary operators by assuming the operator is the first or second token
    # depending on the cursor kind and its typical structure in the AST.
    # For compound assignments and other complex expressions, additional logic may be required.
    tokens = [token.spelling for token in cursor.get_tokens()]
    if cursor.kind in [clang.cindex.CursorKind.BINARY_OPERATOR, clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR]:
        # For binary operators, the operator is typically the second token (after the left operand)
        if len(tokens) >= 2:
            return tokens[1]  # This assumes the operator is the second token
    elif cursor.kind in [clang.cindex.CursorKind.UNARY_OPERATOR, clang.cindex.CursorKind.CONDITIONAL_OPERATOR]:
        # For unary operators, the operator might be the first token
        if tokens:
            return tokens[0]  # This assumes the operator is the first token
    
    return "<unknown_operator>"

def is_literal(cursor_kind):
    # This checks if the cursor kind is among those representing literals in C++
    return cursor_kind in [
        clang.cindex.CursorKind.INTEGER_LITERAL,
        clang.cindex.CursorKind.FLOATING_LITERAL,
        clang.cindex.CursorKind.CHARACTER_LITERAL,
        clang.cindex.CursorKind.STRING_LITERAL,
        # Add other literal kinds as necessary
    ]

def get_literal_value(cursor):
    # Assuming cursor's tokens provide direct access to the literal's textual representation
    tokens = list(cursor.get_tokens())
    if tokens:
        return tokens[0].spelling  # The literal value should be the spelling of the first token
    return "<unknown_literal>"

def is_cin_or_cout(cursor):
    # Checking for member expressions that are calls to cin/cout
    if cursor.kind == clang.cindex.CursorKind.CALL_EXPR or cursor.kind == clang.cindex.CursorKind.CXX_MEMBER_CALL_EXPR:
        tokens = list(cursor.get_tokens())
        if any(t.spelling == "cin" for t in tokens) and any(t.spelling == ">>" for t in tokens):
            return "cin"
        elif any(t.spelling == "cout" for t in tokens) and any(t.spelling == "<<" for t in tokens):
            return "cout"
    return None

def get_sequence(cursor, sequence):
    current = ASTNodeCpp(cursor)
    
    if cursor.location.file is not None and cursor.location.file.name.startswith('/usr/include'):
        return

    current = ASTNodeCpp(cursor)
    token = current.get_token(False)  # False to keep the original case for operators and literals

    if cursor.kind in [
        clang.cindex.CursorKind.BINARY_OPERATOR,
        clang.cindex.CursorKind.UNARY_OPERATOR,
        clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR
        ]:
        operator_symbol = get_operator_symbol(cursor)
        sequence.append(operator_symbol)
    elif is_literal(cursor.kind):
        literal_value = get_literal_value(cursor)
        sequence.append(str(literal_value))
    elif cursor.kind == CursorKind.CXX_TRY_STMT:
        sequence.append('try')
    elif cursor.kind == CursorKind.CXX_CATCH_STMT:
        sequence.append('catch')
    else:
        sequence += [token, cursor.spelling] if cursor.spelling else [token]


    for child_cursor in cursor.get_children():
        get_sequence(child_cursor, sequence)
    
    
    if cursor.kind in [
            CursorKind.FUNCTION_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.CONSTRUCTOR,
            CursorKind.DESTRUCTOR,
            CursorKind.CLASS_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.IF_STMT,
            CursorKind.FOR_STMT,
            CursorKind.WHILE_STMT,
            CursorKind.DO_STMT,
            CursorKind.SWITCH_STMT,
            CursorKind.CXX_TRY_STMT,
            CursorKind.CXX_CATCH_STMT,
            CursorKind.CXX_TRY_STMT,
            CursorKind.CXX_CATCH_STMT
        ]:
        sequence.append('End')

def get_blocks(cursor, block_seq, source_file='test.cpp'):
    
    if cursor.location.file is not None and cursor.location.file.name.startswith('/usr/include'):
        return

    token = (ASTNodeCpp(cursor)).get_token()  # False to not convert token to lowercase
    # Check if the current cursor represents a block-starting structure
    if cursor.kind in [
        CursorKind.BINARY_OPERATOR,
        CursorKind.UNARY_OPERATOR,
        CursorKind.COMPOUND_ASSIGNMENT_OPERATOR
        ]:
        operator_symbol = get_operator_symbol(cursor)
        block_seq.append(operator_symbol)
    if cursor.kind in [
            CursorKind.FUNCTION_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.CONSTRUCTOR,
            CursorKind.DESTRUCTOR,
            CursorKind.CLASS_DECL,
            CursorKind.STRUCT_DECL,
            CursorKind.IF_STMT,
            CursorKind.FOR_STMT,
            CursorKind.WHILE_STMT,
            CursorKind.DO_STMT,
            CursorKind.SWITCH_STMT,
            CursorKind.CXX_TRY_STMT,
            CursorKind.CXX_CATCH_STMT,
            CursorKind.NAMESPACE
        ]:
        block_seq.append(token)
        for child_cursor in cursor.get_children():
            if child_cursor.kind not in [
                    CursorKind.FUNCTION_DECL,
                    CursorKind.CXX_METHOD,
                    CursorKind.CONSTRUCTOR,
                    CursorKind.DESTRUCTOR,
                    CursorKind.CLASS_DECL,
                    CursorKind.STRUCT_DECL,
                    CursorKind.IF_STMT,
                    CursorKind.FOR_STMT,
                    CursorKind.WHILE_STMT,
                    CursorKind.DO_STMT,
                    CursorKind.SWITCH_STMT,
                    CursorKind.CXX_TRY_STMT,
                    CursorKind.CXX_CATCH_STMT,
                    CursorKind.NAMESPACE
                ]:
                block_seq.append((ASTNodeCpp(child_cursor)).get_token())
            get_blocks(child_cursor, block_seq, source_file)
        block_seq.append('End')
    elif cursor.kind == CursorKind.COMPOUND_STMT:
        block_seq.append(token)
        for child_cursor in cursor.get_children():
            if child_cursor.kind not in [
                CursorKind.IF_STMT,
                CursorKind.FOR_STMT,
                CursorKind.WHILE_STMT,
                CursorKind.DO_STMT,
                CursorKind.SWITCH_STMT
                ]:
                block_seq.append((ASTNodeCpp(child_cursor)).get_token())
            get_blocks(child_cursor, block_seq, source_file)
        block_seq.append('End')
    else:
        for child_cursor in cursor.get_children():
            get_blocks(child_cursor, block_seq, source_file)

    # Mark the end of blocks for structures that explicitly define a scope
    # if cursor.kind in [CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD, CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR, CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL, CursorKind.IF_STMT, CursorKind.FOR_STMT, CursorKind.WHILE_STMT, CursorKind.DO_STMT, CursorKind.SWITCH_STMT, CursorKind.CXX_TRY_STMT, CursorKind.CXX_CATCH_STMT, CursorKind.NAMESPACE]:
    #     block_seq.append(token + ' end')