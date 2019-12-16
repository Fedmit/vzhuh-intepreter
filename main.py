import sys

import dill as dill

from lexer import Template, tokenize
from lr_parser import Scanner, Parser
from parser_generator import *
from production import Production
from vzhuh_interpreter import Interpreter


NT = {'GOAL', 'PRG', 'VAR_DECS', 'VAR_DEC', 'STATEMENTS', 'VARS', 'OPS', 'OP', 'IF', 'IF_ELSE', 'BODY',
      'FUNC', 'ARGS', 'ASSIGN', 'EXP', 'OR_EXP', 'AND_EXP', 'TERM', 'P_TERM', 'OPERAND'}

T = {'var', 'type', 'begin', 'end', 'if', 'else', 'then', 'true', 'false', '!', '&', '|', ':', ';', ',', '(', ')',
     '=', 'ident', 'str', '$'}

P = [
    Production('GOAL', 'PRG',                           lambda p: p[0]),
    Production('PRG', 'var VAR_DECS STATEMENTS',        lambda p: ('prg', ('dec', p[1]), p[2])),
    Production('VAR_DECS', 'VAR_DEC VAR_DECS',          lambda p: [p[0]] + p[1]),
    Production('VAR_DECS', 'VAR_DEC',                   lambda p: [p[0]]),
    Production('VAR_DEC', 'VARS : type ;',              lambda p: (p[2], p[0])),
    Production('VARS', 'ident , VARS',                  lambda p: [p[0]] + p[2]),
    Production('VARS', 'ident',                         lambda p: [p[0]]),
    Production('STATEMENTS', 'begin OPS end',           lambda p: ('stmts', p[1])),
    Production('OPS', 'OP OPS',                         lambda p: [p[0]] + p[1]),
    Production('OPS', 'OP',                             lambda p: [p[0]]),
    Production('OP', 'FUNC ;',                          lambda p: p[0]),
    Production('OP', 'ASSIGN ;',                        lambda p: p[0]),
    Production('OP', 'IF',                              lambda p: p[0]),
    Production('OP', 'IF_ELSE',                         lambda p: p[0]),
    Production('IF', 'if EXP then BODY',                lambda p: ('if', p[1], p[3])),
    Production('IF_ELSE', 'if EXP then BODY else BODY', lambda p: ('ifelse', p[1], p[3], p[5])),
    Production('BODY', 'OP',                            lambda p: ('stmts', [p[0]])),
    Production('BODY', 'begin OPS end',                 lambda p: ('stmts', p[1])),
    Production('FUNC', 'ident ( ARGS )',                lambda p: ('call', p[0], p[2])),
    Production('ARGS', 'EXP , ARGS',                    lambda p: [p[0]] + p[2]),
    Production('ARGS', 'EXP',                           lambda p: [p[0]]),
    Production('ASSIGN', 'ident = EXP',                 lambda p: ('=', p[0], p[2])),
    Production('EXP', 'OR_EXP',                         lambda p: p[0]),
    Production('OR_EXP', 'OR_EXP | AND_EXP',            lambda p: ('|', p[0], p[2])),
    Production('OR_EXP', 'AND_EXP',                     lambda p: p[0]),
    Production('AND_EXP', 'AND_EXP & TERM',             lambda p: ('&', p[0], p[2])),
    Production('AND_EXP', 'TERM',                       lambda p: p[0]),
    Production('TERM', '! P_TERM',                      lambda p: ('!', p[1])),
    Production('TERM', 'P_TERM',                        lambda p: p[0]),
    Production('P_TERM', 'OPERAND',                     lambda p: p[0]),
    Production('P_TERM', '( EXP )',                     lambda p: p[1]),
    Production('OPERAND', 'ident',                      lambda p: ('var', p[0])),
    Production('OPERAND', 'str',                        lambda p: ('str', p[0])),
    Production('OPERAND', 'true',                       lambda p: ('const', p[0])),
    Production('OPERAND', 'false',                      lambda p: ('const', p[0]))
]
templates = [
    Template('var', 'var', after=' |\n'),
    Template('type', 'logical|string', after=' |\n|;'),
    Template('begin', 'begin', after=' |\n'),
    Template('end', 'end', after=' |\n|$'),
    Template('if', 'if', after=' |\n'),
    Template('else', 'else', after=' |\n'),
    Template('then', 'then', after=' |\n'),
    Template('true', '1', lambda a: True),
    Template('false', '0', lambda a: False),
    Template('!', '\!'),
    Template('&', '\&'),
    Template('|', '\|'),
    Template(':', ':'),
    Template(';', ';'),
    Template(',', ','),
    Template('(', '\('),
    Template(')', '\)'),
    Template('=', '='),
    Template('ident', '[a-zA-Z]+'),
    Template('str', '".*?"', lambda a: a.strip('"')),
    Template('space', ' +', lambda a: None),
    Template('newline', '\n', lambda a: None),
    Template('comment', '//.*', lambda a: None)
]


def main(filename):
    # print(*P, sep='\n', end='\n\n')

    generator = ParserGenerator(P, T, NT)
    action, goto = generator.load_or_build_tables()

    with open(filename) as file:
        string = ''.join(file.readlines())

    try:
        tokens = tokenize(string, templates)

        scanner = Scanner(tokens)
        parser = Parser(action, goto)
        tree = parser.parse(scanner, T, NT)

        interpreter = Interpreter(tree)
        interpreter.run()

    except Exception as e:
        print(Color.ERROR + 'ERROR: ' + str(e) + Color.ENDC)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('You must specify the path to the source file')
    main(sys.argv[1])
