class Interpreter:
    def __init__(self, tree):
        self.tree = tree

    def run(self):
        print(self._expr(self.tree))

    def _expr(self, tree):
        if tree[0] == 'int':
            return tree[1].value
        elif tree[0] == 'expr' and tree[1].value == 's':
            return self._expr(tree[2]) + self._expr(tree[3])
