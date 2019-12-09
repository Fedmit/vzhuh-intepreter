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
                        _check_var_length(var)
                        self._check_if_already_declared(var)
                        self._vars[var.value] = ('logical', False)
                elif declarations[0].value == 'string':
                    for var in declarations[1]:
                        _check_var_length(var)
                        self._vars[var.value] = ('string', '')
                else:
                    raise Exception('Language does not support type ' + declarations[0].value
                                    + ', line ' + str(declarations[0].line) + ' position ' + str(declarations[0].col))
        else:
            raise Exception('There\'s no declaration of vars')

    def _check_if_already_declared(self, var):
        if var.value in self._vars:
            raise Exception('Variable ' + var.value + ' already declared'
                            + ', line ' + str(var.line) + ' position ' + str(var.col))

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

        elif tree[0] == '=':
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
            if var[0] == 'const':
                raise Exception('Can\'t read into constant, line ' + str(var[1].line)
                                + ' position ' + str(var[1].col))
            elif var[0] == 'var':
                self._is_declared(var[1])
                a = input()
                val = self._vars[var[1].value]
                if val[0] == 'logical':
                    if a == '1':
                        self._vars[var[1].value] = (val[0], True)
                    elif a == '0':
                        self._vars[var[1].value] = (val[0], False)
                    else:
                        raise Exception('Input value must be 1/0')
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
            val = self._compute(exp)
            if val[0] == 'logical':
                if val[1]:
                    print('1', end='')
                else:
                    print('0', end='')
            else:
                print(str(val[1]), end='')

    def _writeln(self, tree):
        if len(tree) > 1:
            raise Exception('Function write() takes only 1 parameter, line ' + str(tree[1][1].line)
                            + ' position ' + str(tree[1][1].col))
        else:
            exp = tree[0]
            val = self._compute(exp)
            if val[0] == 'logical':
                if val[1]:
                    print('1')
                else:
                    print('0')
            else:
                print(str(val[1]))

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
            t, val = self._vars[tree[1].value]
            return tree[1], t, val

        elif tree[0] == 'str':
            return tree[1], 'string', tree[1].value

        elif tree[0] == 'const':
            return tree[1], 'logical', tree[1].value

        elif tree[0] == '|':
            operand1 = self._compute_exp(tree[1])
            operand2 = self._compute_exp(tree[2])
            _is_logical(operand1, operand2)
            return None, 'logical', operand1[2] or operand2[2]

        elif tree[0] == '&':
            operand1 = self._compute_exp(tree[1])
            operand2 = self._compute_exp(tree[2])
            _is_logical(operand1, operand2)
            return None, 'logical', operand1[2] and operand2[2]

        elif tree[0] == '!':
            operand = self._compute_exp(tree[1])
            _is_logical(operand)
            return None, 'logical', not operand[2]

        else:
            raise Exception('There\'s no such operation called ' + tree[0])


def _check_var_length(var):
        if len(var.value) > 11:
            raise Exception('The length of a variable must be 11 or lower'
                            ', line ' + str(var.line) + ' position ' + str(var.col))


def _is_logical(*args):
        for arg in args:
            if arg[1] != 'logical':
                raise Exception('There\'s gotta be logical operand, not ' + arg[1] + ', line ' + str(arg[0].line)
                                + ' position ' + str(arg[0].col))
