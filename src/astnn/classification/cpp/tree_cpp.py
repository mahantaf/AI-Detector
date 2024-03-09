import clang.cindex
from clang.cindex import CursorKind

class ASTNodeCpp:
    def __init__(self, cursor):
        self.cursor = cursor
        self.is_str = isinstance(cursor.spelling, str)
        self.token = self.get_token()
        self.children = self.add_children()

    def is_leaf(self):
        return len(list(self.cursor.get_children())) == 0
    
    def get_token(self, lower=True):
        # Mapping Clang CursorKind to more descriptive tokens
        kind_map = {
            CursorKind.FUNCTION_DECL: "FuncDecl",
            CursorKind.CXX_METHOD: "MethodDecl",
            CursorKind.CONSTRUCTOR: "Constructor",
            CursorKind.DESTRUCTOR: "Destructor",
            CursorKind.IF_STMT: "If",
            CursorKind.FOR_STMT: "For",
            CursorKind.WHILE_STMT: "While",
            CursorKind.DO_STMT: "DoWhile",
            CursorKind.SWITCH_STMT: "Switch",
            CursorKind.CASE_STMT: "Case",
            CursorKind.DEFAULT_STMT: "Default",
            CursorKind.CXX_TRY_STMT: "Try",
            CursorKind.CXX_CATCH_STMT: "Catch",
            CursorKind.CLASS_DECL: "ClassDecl",
            CursorKind.STRUCT_DECL: "StructDecl",
            CursorKind.UNION_DECL: "Union",
            CursorKind.ENUM_DECL: "EnumDecl",
            CursorKind.FIELD_DECL: "FieldDecl",
            CursorKind.VAR_DECL: "VarDecl",
            CursorKind.PARM_DECL: "ParamDecl",
            CursorKind.NAMESPACE: "Namespace",
            CursorKind.TEMPLATE_TYPE_PARAMETER: "TemplateTypeParam",
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER: "TemplateNonTypeParam",
            CursorKind.TEMPLATE_TEMPLATE_PARAMETER: "TemplateTemplateParam",
            # Add more as necessary
        }

        token = kind_map.get(self.cursor.kind, None)

        # Append spelling if present and meaningful
        # if self.cursor.spelling and not token:
        #     token = self.cursor.kind.name + ': ' + self.cursor.spelling
        # elif token and self.cursor.spelling:
        #     token += ': ' + self.cursor.spelling
        
        # Handle cases where the mapping didn't provide a token and spelling isn't useful
        if not token:
            token = self.cursor.kind.name

        return token.lower() if lower else token

    def add_children(self):
        children = []
        for child_cursor in self.cursor.get_children():
            children.append(ASTNodeCpp(child_cursor))
        return children

class SingleNodeCpp(ASTNodeCpp):
    def __init__(self, cursor):
        super().__init__(cursor)
        self.children = []
