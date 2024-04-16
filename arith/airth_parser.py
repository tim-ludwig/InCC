from ply.yacc import yacc
from arith_lexer import tokens, lexer
from arith_ast import *

precedence = [
    ['left', 'OR', 'NOR'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQ', 'NEQ', 'BEQ', 'BNEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE']
]

def p_expression(p):
    """
    expression : arith_expression
               | bool_expression
    """
    p[0] = p[1]

def p_expression_binary(p):
    """
    arith_expression : arith_expression PLUS arith_expression
                     | arith_expression MINUS arith_expression
                     | arith_expression TIMES arith_expression
                     | arith_expression DIVIDE arith_expression
    bool_expression  : arith_expression LT arith_expression
                     | arith_expression GT arith_expression
                     | arith_expression LE arith_expression
                     | arith_expression GE arith_expression
                     | arith_expression EQ arith_expression
                     | arith_expression NEQ arith_expression
                     | bool_expression BEQ bool_expression
                     | bool_expression BNEQ bool_expression
                     | bool_expression AND bool_expression
                     | bool_expression OR bool_expression
                     | bool_expression NAND bool_expression
                     | bool_expression NOR bool_expression
                     | bool_expression IMP bool_expression
    """
    p[0] = binop_expressions[p[2]](p[1], p[3])

def p_expression_unary(p):
    """
    bool_expression : NOT bool_expression
    """
    p[0] = NotExpression(p[2])

def p_expression_num(p):
    'arith_expression : NUMBER'
    p[0] = NumberExpression(p[1])

def p_expression_bool_lit(p):
    'bool_expression : BOOL_LIT'
    p[0] = BoolLiteralExpression(p[1])

def p_expression_paren(p):
    """
    arith_expression : LPAREN arith_expression RPAREN
    bool_expression : LPAREN bool_expression RPAREN
    """
    p[0] = ParenExpression(p[2])


parser = yacc(start='expression')
while True:
    print(parser.parse(input=input("> "), lexer=lexer).eval())