from bcolors import Color
from lexer import Template, tokenize
from lr_parser import *
from mu_interpreter import Interpreter
from parser_generator import *
from production import Production

NT = {'GOAL', 'EXP', 'PRIM'}
T = {'(', 'op', 'int', ')', '$'}

P = [
    Production('GOAL', 'EXP',             lambda p: p[0]),
    Production('EXP', '( op PRIM PRIM )', lambda p: ('expr', p[1], p[2], p[3])),
    Production('PRIM', 'EXP',             lambda p: p[0]),
    Production('PRIM', 'int',             lambda p: ('int', p[0]))
]

templates = [
        Template('(', '\('),
        Template(')', '\)'),
        Template('int', '[1-9][0-9]*', lambda a: int(a)),
        Template('space', ' +', lambda a: None),
        Template('newline', '\n', lambda a: None),
        Template('op', 's', after=' |\n')
    ]


def main():
    print(*P, sep='\n', end='\n\n')

    generator = ParserGenerator(P, T, NT)
    action, goto = generator.build_tables(SHOW_CANONICAL_COL | SHOW_ACTION_TABLE | SHOW_GOTO_TABLE | SHOW_STATISTICS)

    string = '(s 10 (s 5 2))'

    try:
        tokens = tokenize(string, templates, SHOW_TOKENS)

        scanner = Scanner(tokens)
        parser = Parser(action, goto)
        tree = parser.parse(scanner, T, NT, SHOW_TREE | SHOW_STEPS)

        interpreter = Interpreter(tree)
        interpreter.run()

    except Exception as e:
        print(Color.ERROR + 'ERROR: ' + str(e) + Color.ENDC)


if __name__ == '__main__':
    main()
