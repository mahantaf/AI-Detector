from javalang.ast import Node

class BlockNode(object):
    def __init__(self, node):
        self.node = node
        self.is_str = isinstance(self.node, str)
        self.token = self.get_token(node)
        self.children = self.add_children()

    def is_leaf(self):
        if self.is_str:
            return True
        return len(self.node.children) == 0

    def get_token(self, node):
        if isinstance(node, str):
            token = node
        elif isinstance(node, set):
            token = 'Modifier'
        elif isinstance(node, Node):
            token = node.__class__.__name__
        else:
            token = ''
        return token

    def ori_children(self, root):
        if isinstance(root, Node):
            if self.token in ['MethodDeclaration', 'ConstructorDeclaration']:
                children = root.children[:-1]
            else:
                children = root.children
        elif isinstance(root, set):
            children = list(root)
        else:
            children = []

        def expand(nested_list):
            for item in nested_list:
                if isinstance(item, list):
                    for sub_item in expand(item):
                        yield sub_item
                elif item:
                    yield item

        return list(expand(children))

    def add_children(self):
        if self.is_str:
            return []
        logic = ['SwitchStatement', 'IfStatement', 'ForStatement', 'WhileStatement', 'DoStatement']
        children = self.ori_children(self.node)
        if self.token in logic:
            return [BlockNode(children[0])]
        elif self.token in ['MethodDeclaration', 'ConstructorDeclaration']:
            return [BlockNode(child) for child in children]
        else:
            return [BlockNode(child) for child in children if self.get_token( child) not in logic]