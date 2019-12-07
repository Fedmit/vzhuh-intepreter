import re

from flags import SHOW_TOKENS


class Token(object):
    def __init__(self, name, value, start, end, line, col):
        self.name = name
        self.value = value
        self.start = start
        self.end = end
        self.line = line
        self.col = col

    def __eq__(self, other):
        return self.name == other

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return '(' + self.name + ', "' + str(self.value) + '"' + ')'

    def __repr__(self):
        return str(self.value)


class Template(object):
    def __init__(self, name, regexp, process=None):
        self.name = name
        r = re.compile(regexp)
        self.regexp = r
        self.process = process

    def match(self, string, start, line, col):
        matched = self.regexp.match(string, start)
        if not matched:
            return False

        end = matched.end()

        if self.process:
            value = self.process(matched.group())
        else:
            value = matched.group()

        for c in matched.group():
            if c == '\n':
                line += 1
                col = 1

        return Token(self.name, value, start, end, line, col)


def tokenize(string, templates, debug_flags=None):
    start = 0
    tokens = []
    line = 1
    col = 1

    if string == '':
        return []

    while True:
        valid = False

        for tp in templates:
            token = tp.match(string, start, line, col)
            if not token:
                continue

            if token.value is not None:
                tokens.append(token)

            start = token.end
            valid = True
            if token.line != line:
                col = 1
            else:
                col += token.end - token.start
            line = token.line
            break

        if not valid:
            raise Exception("Token error at position " + str(col) + " on line " + str(line) + '.')

        if start == len(string):
            tokens += [Token('$', '$', -1, -1, line, col)]
            if debug_flags and (debug_flags & SHOW_TOKENS) == SHOW_TOKENS:
                print(*tokens, sep='\n', end='\n\n')

            return tokens
