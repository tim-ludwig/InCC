# type: ignore
# ignore name conflict
from ply import yacc
from lexer.lexer import tokens, lexer

from parser.literals import *
from parser.operators import *
from parser.variables import *
from parser.sequences import *
from parser.controlflow import *
from parser.functions import *


precedence = [
    ['nonassoc', 'THEN'],
    ['nonassoc', 'ELSE', 'DO', 'WHILE', 'IN'],
    ['left', 'COMMA'],
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
    ['right', 'LPAREN', 'LBRACKET'],
]


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p}")


parser = yacc.yacc(start='expression')


def parse_expr(text: str) -> Expression:
    return parser.parse(input=text, lexer=lexer)
