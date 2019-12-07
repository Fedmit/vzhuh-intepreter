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
        if tree[0] == 'dec':
            for declarations in tree[1]:
                if declarations[0].value == 'logical':
                    for var in declarations[1]:
                        self._vars[var.value] = ('logical', False)
                elif declarations[0].value == 'string':
                    for var in declarations[1]:
                        self._vars[var.value] = ('string', '')
                else:
                    raise Exception('Language does not support type ' + declarations[0].value
                                    + ', line ' + str(declarations[0].line) + ' position ' + str(declarations[0].col))
        else:
            raise Exception('There\'s no declaration of vars')

    def _compute_operations(self, tree):
        if tree[0] == 'statements':
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
            elif tree[1].value == 'writeln':
                self._writeln(tree[2])
            else:
                raise Exception('There\'s no such function called ' + tree[1].value
                                + ' at line ' + str(tree[1].line) + ' position '
                                + str(tree[1].col) + ' is not declared')

        elif tree[0] == 'assign':
            self._assign(tree)

        elif tree[0] == 'if' or tree[0] == 'ifelse':
            self._if_else(tree)

        else:
            raise Exception('There\'s no such operation called ' + tree[0])

    def _if_else(self, tree):
        val = self._compute(tree[1])
        if val[0] != 'logical':
            raise Exception('If operator takes only logical, not ' + val[0] + ', line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))

        if val[1]:
            for operation in tree[2]:
                self._compute_operation(operation)
        elif tree[0] == 'ifelse':
            for operation in tree[3]:
                self._compute_operation(operation)

    def _is_declared(self, var):
        if var.value not in self._vars:
            raise Exception('Variable ' + var.value + ' at line ' + str(var.line)
                            + ' position ' + str(var.col) + ' is not declared')

    def _read(self, tree):
        if len(tree) > 1:
            raise Exception('Function read() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            var = tree[0]
            val = self._vars[var[1].value]
            if var[0] == 'const':
                raise Exception('Can\'t read into constant, line ' + str(var[1].line)
                                + ' position ' + str(var[1].col))
            elif var[0] == 'var':
                self._is_declared(var[1])
                a = input()
                if val[0] == 'logical':
                    if a == 'true':
                        self._vars[var[1].value] = (val[0], True)
                    elif a == 'false':
                        self._vars[var[1].value] = (val[0], False)
                    else:
                        raise Exception('Input value must be true/false')
                elif val[0] == 'string':
                    self._vars[var[1].value] = (val[0], a)
                else:
                    raise Exception('Language does not support type ' + val[0])
            else:
                raise Exception('There\'s no such operand called ' + var[0])

    def _write(self, tree):
        if len(tree) > 1:
            raise Exception('Function write() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            exp = tree[0]
            print(str(self._compute(exp)[1]), end='')

    def _writeln(self, tree):
        if len(tree) > 1:
            raise Exception('Function write() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            exp = tree[0]
            print(str(self._compute(exp)[1]))

    def _assign(self, tree):
        self._is_declared(tree[1])
        val = self._compute(tree[2])
        var = self._vars[tree[1].value]
        if val[0] == var[0]:
            self._vars[tree[1].value] = val
        else:
            raise Exception('Can\'t assign ' + val[0] + ' to variable ' + tree[1].value + ' of type ' + var[0]
                            + ', line ' + str(tree[1].line) + ' position ' + str(tree[1].col))

    def _compute(self, tree):
        val = self._compute_exp(tree)
        return val[1], val[2]

    def _compute_exp(self, tree):
        if tree[0] == 'var':
            self._is_declared(tree[1])
            type, val = self._vars[tree[1].value]
            return tree[1], type, val

        elif tree[0] == 'str':
            return tree[1], 'string', tree[1].value

        elif tree[0] == 'const':
            return tree[1], 'logical', tree[1].value

        elif tree[0] == 'or':
            operand1 = self._compute_exp(tree[1])
            operand2 = self._compute_exp(tree[2])
            _is_logical(operand1, operand2)
            return None, 'logical', operand1[2] or operand2[2]

        elif tree[0] == 'and':
            operand1 = self._compute_exp(tree[1])
            operand2 = self._compute_exp(tree[2])
            _is_logical(operand1, operand2)
            return None, 'logical', operand1[2] and operand2[2]

        elif tree[0] == 'not':
            operand = self._compute_exp(tree[1])
            _is_logical(operand)
            return None, 'logical', not operand[2]

        else:
            raise Exception('There\'s no such operation called ' + tree[0])


def _is_logical(*args):
        for arg in args:
            if arg[1] != 'logical':
                raise Exception('There\'s gotta be logical operand, not ' + arg[1] + ', line ' + str(arg[0].line)
                                + ' position ' + str(arg[0].col))
