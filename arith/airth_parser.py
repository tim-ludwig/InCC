from ply.yacc import yacc
from arith_lexer import tokens, lexer
from arith_ast import *

precedence = [
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQS', 'NEQS', 'EQ', 'NEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE']
]

def p_expression_binary(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression LT expression
               | expression GT expression
               | expression LE expression
               | expression GE expression
               | expression EQS expression
               | expression NEQS expression
               | expression EQ expression
               | expression NEQ expression
               | expression AND expression
               | expression OR expression
               | expression NAND expression
               | expression NOR expression
               | expression IMP expression
               | expression XOR expression
    '''
    p[0] = BinaryOperator(p[2], p[1], p[3])

def p_expression_unary(p):
    'expression : NOT expression'
    p[0] = NotExpression(p[2])

def p_expression_num(p):
    'expression : NUMBER'
    p[0] = NumberExpression(p[1])

def p_expression_bool_lit(p):
    '''
    expression : TRUE
               | FALSE
    '''
    p[0] = BoolLiteralExpression(p[1])

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = ParenExpression(p[2])

parser = yacc(start='expression')
while True:
    ast = parser.parse(input=input("> "), lexer=lexer)

    try:
        ast.typecheck()
        print(ast.s_expression())
        print(ast.eval())
    except TypeError as error:
        print('TypeError')
        print(error)