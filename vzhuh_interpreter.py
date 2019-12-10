from lexer import Token


class Interpreter:
    _vars = {}

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        self.next_node(self.tree)

    def next_node(self, tree):
        name = tree[0]
        if isinstance(name, Token):
            name = name.value
        return _nodes.get(name, None)(self, *tree[1:])

    def compute_program(self, dec, stmts):
        self.next_node(dec)
        self.next_node(stmts)

    def compute_declaration(self, types):
        for var_list in types:
            self.next_node(var_list)

    def declare_logical(self, var_list):
        for var in var_list:
            _check_var_length(var)
            self._check_if_already_declared(var)
            self._vars[var.value] = ('logical', False)

    def declare_string(self, var_list):
        for var in var_list:
            _check_var_length(var)
            self._vars[var.value] = ('string', '')

    def _check_if_already_declared(self, var):
        if var.value in self._vars:
            raise Exception('Variable ' + var.value + ' already declared'
                            + ', line ' + str(var.line) + ' position ' + str(var.col))

    def compute_operations(self, operations):
        for operation in operations:
            self.next_node(operation)

    def compute_function(self, name, args):
        try:
            _functions[name.value](self, args)
        except KeyError:
            raise Exception('There\'s no such function called ' + name.value
                            + ' at line ' + str(name.line) + ' position '
                            + str(name.col) + ' is not declared')

    def compute_if(self, expr, true):
        res = self.compute_expr(expr)
        if res.type != 'logical':
            raise Exception('If operator takes only logical, not ' + res.type + ', line ' + str(expr[1].line)
                            + ' position ' + str(expr[1].col))

        if res.value:
            self.next_node(true)

    def compute_ifelse(self, expr, true, false):
        res = self.compute_expr(expr)
        if res.type != 'logical':
            raise Exception('If operator takes only logical, not ' + res.type + ', line ' + str(expr[1].line)
                            + ' position ' + str(expr[1].col))

        if res.value:
            self.next_node(true)
        else:
            self.next_node(false)

    def _is_declared(self, var):
        if var.value not in self._vars:
            raise Exception('Variable ' + var.value + ' at line ' + str(var.line)
                            + ' position ' + str(var.col) + ' is not declared')

    def function_read(self, args):
        if len(args) > 1:
            raise Exception('Function read() takes only 1 parameter, line ' + str(args[1][1].line)
                            + ' position ' + str(args[1][1].col))
        else:
            var = args[0]
            res = self.compute_expr(var)
            if var[0] == 'var':
                a = input()
                if res.type == 'logical':
                    if a == '1':
                        self._vars[var[1].value] = (res.type, True)
                    elif a == '0':
                        self._vars[var[1].value] = (res.type, False)
                    else:
                        raise Exception('Input value must be 1/0')
                elif res.type == 'string':
                    self._vars[var[1].value] = (res.type, a)
                else:
                    raise Exception('Language does not support type ' + res.type)
            else:
                raise Exception('Read function takes only variable, line ' + str(res.line)
                                + ' position ' + str(res.col))

    def function_write(self, args):
        self._write(args, '')

    def function_writeln(self, args):
        self._write(args, '\n')

    def _write(self, args, end):
        if len(args) > 1:
            raise Exception('Function write() takes only 1 parameter, line ' + str(args[1][1].line)
                            + ' position ' + str(args[1][1].col))
        else:
            expr = args[0]
            res = self.compute_expr(expr)
            if res.type == 'logical':
                if res.value:
                    print('1', end=end)
                else:
                    print('0', end=end)
            else:
                print(str(res.value), end=end)

    def compute_assign(self, left, expr):
        self._is_declared(left)
        res = self.compute_expr(expr)
        var = self._vars[left.value]
        if res.type == var[0]:
            self._vars[left.value] = (res.type, res.value)
        else:
            raise Exception('Can\'t assign ' + res.type + ' to variable ' + left.value + ' of type ' + var[0]
                            + ', line ' + str(left.line) + ' position ' + str(left.col))

    def compute_expr(self, expr):
        return self.next_node(expr)

    def compute_var(self, name):
        self._is_declared(name)
        t, val = self._vars[name.value]
        return Result(t, val, name.line, name.col)

    def compute_str(self, name):
        return Result('string', name.value, name.line, name.col)

    def compute_const(self, name):
        return Result('logical', name.value, name.line, name.col)

    def compute_or(self, arg1, arg2):
        val1 = self.next_node(arg1)
        val2 = self.next_node(arg2)
        val1.value = bool(val2 or val1)
        return val1

    def compute_and(self, arg1, arg2):
        val1 = self.next_node(arg1)
        val2 = self.next_node(arg2)
        val1.value = bool(val2 and val1)
        return val1

    def compute_not(self, arg1):
        val1 = self.next_node(arg1)
        val1.value = bool(not val1)
        return val1


class Result:
    def __init__(self, t, value, line=None, col=None):
        self.type = t
        self.value = value
        self.line = line
        self.col = col

    def __bool__(self):
        if self.type != 'logical':
            raise Exception('There\'s gotta be logical operand, not ' + self.type + ', line ' + str(self.line)
                            + ' position ' + str(self.col))
        return self.value

    def __repr__(self):
        return '(' + self.type + ', ' + str(self.value) + ')'


def _check_var_length(var):
        if len(var.value) > 11:
            raise Exception('The length of a variable must be 11 or lower'
                            ', line ' + str(var.line) + ' position ' + str(var.col))


_nodes = {
        'prg': Interpreter.compute_program,
        'dec': Interpreter.compute_declaration,
        'logical': Interpreter.declare_logical,
        'string': Interpreter.declare_string,
        'stmts': Interpreter.compute_operations,
        'call': Interpreter.compute_function,
        '=': Interpreter.compute_assign,
        'if': Interpreter.compute_if,
        'ifelse': Interpreter.compute_ifelse,
        'var': Interpreter.compute_var,
        'str': Interpreter.compute_str,
        'const': Interpreter.compute_const,
        '|': Interpreter.compute_or,
        '&': Interpreter.compute_and,
        '!': Interpreter.compute_not,
}

_functions = {
        'read': Interpreter.function_read,
        'write': Interpreter.function_write,
        'writeln': Interpreter.function_writeln
}
