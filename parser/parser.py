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
from parser.struct import *
from parser.module import *


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
    ['right', 'LPAREN', 'LBRACKET', 'DOT'],
]


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p}")


def p_trap(p):
    """
    expression : TRAP
    """
    p[0] = TrapExpression()



parser = yacc.yacc(start='expression')


def parse_expr(text: str) -> Expression:
    return parser.parse(input=text, lexer=lexer)
