import argparse
import parser # type: ignore
from environment import Environment

argparser = argparse.ArgumentParser(prog ='interpreter', description='Run the interpreter')
argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')

if __name__ == '__main__':
    args = argparser.parse_args()
    env = Environment()

    if args.file:
        with open(args.file, 'r') as f:
            parser.parse(f.read()).eval(env)

    if args.repl:
        while True:
            print(parser.parse(input("> ")).eval(env))