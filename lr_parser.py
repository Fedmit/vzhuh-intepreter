import pprint
from collections import deque

from tabulate import tabulate

from flags import *
from lexer import Token
from tables import Shift, Reduce, Accept


class Parser:
    _steps = []

    def __init__(self, action, goto):
        self._action = action
        self._goto = goto

    def parse(self, scanner, T, NT, debug_flags=None):
        try:
            tree = self._parse(scanner, T, NT)
        finally:
            if debug_flags and (debug_flags & SHOW_STEPS) == SHOW_STEPS:
                print(self._steps_table())

        if debug_flags and (debug_flags & SHOW_TREE) == SHOW_TREE:
            pprint.pprint(tree)
            print()
        return tree

    def _parse(self, scanner, T, NT):
        scanner.reset()
        self._steps = []
        stack = deque()
        tree_stack = deque()

        stack.append(0)
        token = scanner.next_token()
        while True:
            s = stack[-1]
            if isinstance(self._action.get(s, token.name), Shift):
                shift = self._action.get(s, token.name)

                self._record(stack, scanner.get_last_input(), shift)

                stack.append(token)
                stack.append(shift.state)
                token = scanner.next_token()

            elif isinstance(self._action.get(s, token.name), Reduce):
                reduce = self._action.get(s, token.name)

                self._record(stack, scanner.get_last_input(), reduce)

                rhs = []
                for i in range(2 * len(reduce.p.rhs)):
                    t_nt = stack.pop()
                    if i % 2 == 1:
                        if t_nt in NT:
                            rhs += [tree_stack.pop()]
                        elif t_nt in T:
                            rhs += [t_nt]
                rhs.reverse()
                tree_stack.append(reduce.p.process(rhs))

                s = stack[-1]
                stack.append(reduce.p.lhs)
                stack.append(self._goto.get(s, reduce.p.lhs))

            elif isinstance(self._action.get(s, token.name), Accept) and token.name == '$':
                accept = self._action.get(s, token.name)
                self._record(stack, scanner.get_last_input(), accept)

                return tree_stack.pop()

            else:
                self._record(stack, scanner.get_last_input(), 'err')

                raise Exception(
                    'Unexpected ' + str(token.value) + ' at line ' + str(token.line)
                    + ' position ' + str(token.col) + '.')

    def _record(self, stack, last_input, action):
        self._steps += [Step(stack, last_input, action)]

    def _steps_table(self):
        header = ['step', 'stack', 'input', 'action']
        rows = []
        for step in range(len(self._steps)):
            s = self._steps[step]
            rows += [[str(step), s.stack, s.last_input, str(s.action)]]

        return 'Steps\n' + tabulate(rows, headers=header, tablefmt='psql') + '\n'


class Scanner:
    _head = -1

    def __init__(self, tokens):
        self._tokens = tokens

    def reset(self):
        self._head = -1

    def next_token(self):
        self._head += 1
        return self._tokens[self._head]

    def get_last_input(self):
        return self._tokens[self._head:]


class Step:
    def __init__(self, stack, last_input, action):
        _stack = []
        for i in stack:
            if isinstance(i, Token):
                _stack += [str(i.name)]
            else:
                _stack += [str(i)]
        self.stack = ' '.join(_stack)
        self.last_input = ' '.join([str(i.name) for i in last_input])
        self.action = action
