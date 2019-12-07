from enum import Enum

from vzhuh_interpreter import Interpreter
from lexer import Template, tokenize
from lr_parser import Scanner, Parser
from parser_generator import *
from production import Production

# noinspection PyArgumentList
NT = Enum('NT', 'GOAL PRG VAR_DEC COMPS VARS OPS FUNC ARGS ASSIGN EXP OR_EXP AND_EXP TERM P_TERM OPERAND')
T = ['var', 'type', 'begin', 'end', 'true', 'false', '!', '&', '|', ':', ';', ',', '(', ')', '=', 'ident', '$']

P = [
    Production(NT.GOAL, (NT.PRG,), lambda p: p[0]),
    Production(NT.PRG, (NT.VAR_DEC, NT.COMPS),                 lambda p: ('program', p[0], p[1])),
    Production(NT.VAR_DEC, ('var', NT.VARS, ':', 'type', ';'), lambda p: ('declaration', p[3], p[1])),
    Production(NT.VARS, ('ident', ',', NT.VARS),               lambda p: [p[0]] + p[2]),
    Production(NT.VARS, ('ident',),                            lambda p: [p[0]]),
    Production(NT.COMPS, ('begin', NT.OPS, 'end'),             lambda p: ('operations', p[1])),
    Production(NT.OPS, (NT.FUNC, ';', NT.OPS),                 lambda p: [p[0]] + p[2]),
    Production(NT.OPS, (NT.FUNC, ';'),                         lambda p: [p[0]]),
    Production(NT.OPS, (NT.ASSIGN, ';', NT.OPS),               lambda p: [p[0]] + p[2]),
    Production(NT.OPS, (NT.ASSIGN, ';'),                       lambda p: [p[0]]),
    Production(NT.FUNC, ('ident', '(', NT.ARGS, ')'),          lambda p: ('call', p[0], p[2])),
    Production(NT.ARGS, (NT.OPERAND, ',', NT.ARGS),            lambda p: [p[0]] + p[2]),
    Production(NT.ARGS, (NT.OPERAND,),                         lambda p: [p[0]]),
    Production(NT.ASSIGN, ('ident', '=', NT.EXP),              lambda p: ('assign', p[0], p[2])),
    Production(NT.EXP, (NT.OR_EXP,),                           lambda p: p[0]),
    Production(NT.OR_EXP, (NT.OR_EXP, '|', NT.AND_EXP),        lambda p: ('or', p[0], p[2])),
    Production(NT.OR_EXP, (NT.AND_EXP,),                       lambda p: p[0]),
    Production(NT.AND_EXP, (NT.AND_EXP, '&', NT.TERM),         lambda p: ('and', p[0], p[2])),
    Production(NT.AND_EXP, (NT.TERM,),                         lambda p: p[0]),
    Production(NT.TERM, ('!', NT.P_TERM),                      lambda p: ('not', p[1])),
    Production(NT.TERM, (NT.P_TERM,),                          lambda p: p[0]),
    Production(NT.P_TERM, (NT.OPERAND,),                       lambda p: p[0]),
    Production(NT.P_TERM, ('(', NT.EXP, ')'),                  lambda p: p[1]),
    Production(NT.OPERAND, ('ident',),                         lambda p: ('var', p[0])),
    Production(NT.OPERAND, ('true',),                          lambda p: ('const', p[0])),
    Production(NT.OPERAND, ('false',),                         lambda p: ('const', p[0]))
]
templates = [
    Template('var', 'var'),
    Template('type', 'logical'),
    Template('begin', 'begin'),
    Template('end', 'end'),
    Template('true', 'true', lambda a: True),
    Template('false', 'false', lambda a: False),
    Template('!', '\!'),
    Template('&', '\&'),
    Template('|', '\|'),
    Template(':', ':'),
    Template(';', ';'),
    Template(',', ','),
    Template('(', '\('),
    Template(')', '\)'),
    Template('=', '='),
    Template('ident', '\w+'),
    Template('space', ' +', lambda a: None),
    Template('newline', '\n', lambda a: None),
    Template('comment', '#.*', lambda a: None)
]


def main():
    print(*P, sep='\n', end='\n\n')

    generator = ParserGenerator(P, T, NT)
    action, goto = generator.build_tables(SHOW_CANONICAL_COL | SHOW_ACTION_TABLE | SHOW_GOTO_TABLE)

    with open("source.txt") as file:
        string = ''.join(file.readlines())

    tokens = tokenize(string, templates)

    scanner = Scanner(tokens)
    parser = Parser(action, goto)
    tree = parser.parse(scanner, SHOW_TREE)

    interpreter = Interpreter(tree)
    interpreter.run()


if __name__ == '__main__':
    main()
