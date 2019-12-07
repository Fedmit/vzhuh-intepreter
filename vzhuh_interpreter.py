class Interpreter:
    _vars = {}

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        if self.tree[0] == 'program':
            self._declare_vars(self.tree[1])
            self._compute_operations(self.tree[2])
        else:
            raise Exception('There\'s no program')

    def _declare_vars(self, tree):
        if tree[0] == 'declaration':
            if tree[1].value == 'logical':
                for var in tree[2]:
                    self._vars[var.value] = False
            else:
                raise Exception('Language supports only LOGICAL type, line ' + str(tree[1].line)
                                + ' position ' + str(tree[1].col))
        else:
            raise Exception('There\'s no declaration of vars')

    def _compute_operations(self, tree):
        if tree[0] == 'operations':
            for operation in tree[1]:
                self._compute_operation(operation)
        else:
            raise Exception('There\'s no operations')

    def _compute_operation(self, tree):
        if tree[0] == 'call':
            if tree[1].value == 'read':
                self._read(tree[2])
            elif tree[1].value == 'write':
                self._write(tree[2])
            else:
                raise Exception('There\'s no such function called ' + tree[1].value
                                + ' at line ' + str(tree[1].line) + ' position '
                                + str(tree[1].col) + ' is not declared')
        elif tree[0] == 'assign':
            self._assign(tree)
        else:
            raise Exception('There\'s no such operation called ' + tree[0])

    def _check_variable(self, var):
        if var.value not in self._vars:
            raise Exception('Variable ' + var.value + ' at line ' + str(var.line)
                            + ' position ' + str(var.col) + ' is not declared')

    def _read(self, tree):
        if len(tree) > 1:
            raise Exception('Function read() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            var = tree[0]
            if var[0] == 'const':
                raise Exception('Can\'t read into constant, line ' + str(var[1].line)
                                + ' position ' + str(var[1].col))
            elif var[0] == 'var':
                self._check_variable(var[1])
                a = input()
                if a == 'true':
                    self._vars[var[1].value] = True
                elif a == 'false':
                    self._vars[var[1].value] = False
                else:
                    raise Exception('Input value must be true/false')
            else:
                raise Exception('There\'s no such operand called ' + var[0])

    def _write(self, tree):
        if len(tree) > 1:
            raise Exception('Function write() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            var = tree[0]
            if var[0] == 'const':
                print(str(var[1].value))
            elif var[0] == 'var':
                self._check_variable(var[1])
                print(str(self._vars[var[1].value]))
            else:
                raise Exception('There\'s no such operand called ' + var[0])

    def _assign(self, tree):
        self._check_variable(tree[1])
        self._vars[tree[1].value] = self._compute(tree[2])

    def _compute(self, tree):
        if tree[0] == 'var':
            self._check_variable(tree[1])
            return self._vars[tree[1].value]
        elif tree[0] == 'const':
            return tree[1].value
        elif tree[0] == 'or':
            return self._compute(tree[1]) or self._compute(tree[2])
        elif tree[0] == 'and':
            return self._compute(tree[1]) and self._compute(tree[2])
        elif tree[0] == 'not':
            return not self._compute(tree[1])
        else:
            raise Exception('There\'s no such operation called ' + tree[0])
