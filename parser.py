# type: ignore
# ignore name conflict
from ply import yacc
from lexer import tokens, lexer

from literals_parser import *
from operators_parser import *
from variables_parser import *
from sequences_parser import *
from controlflow_parser import *
from lambda_parser import *

from environment import Environment

precedence = [
    ['nonassoc', 'THEN'],
    ['nonassoc', 'ELSE', 'DO', 'WHILE', 'IN'],
    ['right', 'ASSIGN'],
    ['right', 'RIGHT_ARROW'],
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
parser.parse(input='counter := val -> inc -> val := val + inc', lexer=lexer).eval(env)
parser.parse(input='fac := local f := (x -> if x = 0 then 1 else x * f(x - 1)) in f', lexer=lexer).eval(env)
while True:
    ast = parser.parse(input=input("> "), lexer=lexer)
    result = ast.eval(env)
    print(result)
    print('Variables: ', env)