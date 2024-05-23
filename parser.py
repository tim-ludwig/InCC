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
    ['right', 'LPAREN'],
]

def p_error(p):
    raise SyntaxError(f"Syntax error at token {p}")

parser = yacc.yacc(start='expression')

def parse(input: str) -> Expression:
    return parser.parse(input=input, lexer=lexer)