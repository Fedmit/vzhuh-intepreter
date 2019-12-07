from lexer import Template, tokenize
from lr_parser import *
from mu_interpreter import Interpreter
from parser_generator import *
from production import Production

# noinspection PyArgumentList
NT = Enum('NT', 'GOAL EXP PRIM')
T = ['(', 'op', 'int', ')', '$']

P = [
    Production(NT.GOAL, (NT.EXP,),                         lambda p: p[0]),
    Production(NT.EXP, ('(', 'op', NT.PRIM, NT.PRIM, ')'), lambda p: ('expr', p[1], p[2], p[3])),
    Production(NT.PRIM, (NT.EXP,),                         lambda p: p[0]),
    Production(NT.PRIM, ('int',),                          lambda p: ('int', p[0]))
]

templates = [
        Template('(', '\('),
        Template(')', '\)'),
        Template('int', '[1-9][0-9]*', lambda a: int(a)),
        Template('space', ' +', lambda a: None),
        Template('newline', '\n', lambda a: None),
        Template('op', 's ', lambda a: a.rstrip())
    ]


def main():
    print(*P, sep='\n', end='\n\n')

    generator = ParserGenerator(P, T, NT)
    action, goto = generator.build_tables(SHOW_CANONICAL_COL | SHOW_ACTION_TABLE | SHOW_GOTO_TABLE)

    string = '(s 10 (s 5 2))'

    tokens = tokenize(string, templates)

    scanner = Scanner(tokens)
    parser = Parser(action, goto)
    tree = parser.parse(scanner, SHOW_TREE | SHOW_STEPS)

    interpreter = Interpreter(tree)
    interpreter.run()


if __name__ == '__main__':
    main()
