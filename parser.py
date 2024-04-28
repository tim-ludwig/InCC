from ply import yacc
from lexer import tokens, lexer
from operators_parser import *

precedence = [
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'IMP'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQS', 'NEQS', 'EQ', 'NEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE'],
    ['right', 'NOT', 'UMINUS', 'UPLUS']
]

parser = yacc.yacc(start='expression')
while True:
    ast = parser.parse(input=input("> "), lexer=lexer)

    try:
        ast.typecheck()
        print(ast.s_expression())
        print(ast.eval())
    except TypeError as error:
        print('TypeError')
        print(error)