import argparse
from parser import parser # type: ignore
from environment import Environment


argparser = argparse.ArgumentParser(prog ='interpreter', description='Run the interpreter')
argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')


if __name__ == '__main__':
    args = argparser.parse_args()
    env = Environment()

    if args.file:
        with (open(args.file, 'r') as f):
            inp = f.read()
            ast = parser.parse(inp)
            ast.eval(env)

    if args.repl:
        while True:
            inp = input("> ")
            ast = parser.parse(inp)
            res = ast.eval(env)
            print(res)
