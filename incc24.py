#! /usr/bin/python

import argparse

from interpreter import interpreter
from compiler import compiler

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='InCC24', description='CLI tool for the InCC24 language')

    subparsers = argparser.add_subparsers(required=True, dest='action', title='Actions')

    action_interpret = subparsers.add_parser('interpret', help='run the interpreter', aliases=['i'])
    action_interpret.add_argument('file', type=str, nargs='?', help='The file to interpret')
    action_interpret.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')
    action_interpret.add_argument('--stop-on-error', action='store_true', help='Stop the repl on error')

    action_compile = subparsers.add_parser('compile', help='run the compiler', aliases=['c'])
    action_compile.add_argument('file', type=str, help='The file to compile')
    action_compile.add_argument('-o', dest='outfile', type=str, default='-', help='Set output file. - for stdout')
    action_compile.add_argument('--vm', type=str, choices=['cma', 'mama', 'ima24'], default='mama', help='which VM to use')
    action_compile.add_argument('--emit', '-e', choices=['ir', 'asm', 'obj', 'exe'], help='Determine output stage. If unspecified, output stage is determined by type of output file.')
    action_compile.add_argument('--keep-asm', action='store_true', help="don't delete the intermediate asm file")

    args = argparser.parse_args()

    match args.action:
        case 'interpret' | 'i':
            if args.stop_on_error and not args.repl:
                argparser.error('--stop-on-error requires --repl')

            interpreter.main(args)

        case 'compile' | 'c':
            if args.outfile == '-' and args.emit is None:
                argparser.error('writing to stdout requires --emit')

            compiler.main(args)
