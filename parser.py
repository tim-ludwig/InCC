# type: ignore
# ignore name conflict
from ply import yacc
from lexer import tokens, lexer

from literals_parser import *
from operators_parser import *
from variables_parser import *
from sequences_parser import *
from controlflow_parser import *

from environment import Environment

precedence = [
    ['nonassoc', 'THEN'],
    ['nonassoc', 'ELSE', 'DO', 'WHILE', 'IN'],
    ['right', 'ASSIGN'],
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'IMP'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQS', 'NEQS', 'EQ', 'NEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE'],
    ['right', 'NOT', 'UMINUS', 'UPLUS'],
]

parser = yacc.yacc(start='expression')
env = Environment()
while True:
    try:
        ast = parser.parse(input=input("> "), lexer=lexer)
        env = ast.typecheck(env)
        result, env = ast.eval(env)
        print(result)
        print('Variables: ', env)
    except TypeError as e:
        print(e)