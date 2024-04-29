# type: ignore
# ignore name conflict
from ply import yacc
from lexer import tokens, lexer

from literals_parser import *
from operators_parser import *
from variables_parser import *
from sequences_parser import *
from controlflow_parser import *

precedence = [
    ['right', 'ASSIGN'],
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'IMP'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQS', 'NEQS', 'EQ', 'NEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE'],
    ['right', 'NOT', 'UMINUS', 'UPLUS'],
    ['right', 'ELSE']
]

parser = yacc.yacc(start='expression')
env = {}
vars = {}
while True:
    ast = parser.parse(input=input("> "), lexer=lexer)
    vars = ast.typecheck(vars)
    result, env = ast.eval(env)
    print(result)
    print('Variables: ', env)