from ply.yacc import yacc
from arith_lexer import tokens, lexer
from arith_ast import *

precedence = [
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQ', 'NEQ'],
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

def p_expression_plus(p):
    'arith_expression : arith_expression PLUS arith_expression'
    p[0] = PlusExpression(p[1], p[3])

def p_expression_minus(p):
    'arith_expression : arith_expression MINUS arith_expression'
    p[0] = MinusExpression(p[1], p[3])

def p_expression_times(p):
    'arith_expression : arith_expression TIMES arith_expression'
    p[0] = TimesExpression(p[1], p[3])

def p_expression_divide(p):
    'arith_expression : arith_expression DIVIDE arith_expression'
    p[0] = DivideExpression(p[1], p[3])

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

def p_expression_eq(p):
    """
    arith_expression : arith_expression EQ arith_expression
    bool_expression : bool_expression EQ bool_expression
    """
    p[0] = EqualExpression(p[1], p[3])

def p_expression_neq(p):
    """
    arith_expression : arith_expression NEQ arith_expression
    bool_expression : bool_expression NEQ bool_expression
                    | bool_expression XOR bool_expression
    """
    p[0] = NotEqualExpression(p[1], p[3])

def p_expression_lt(p):
    'bool_expression : arith_expression LT arith_expression'
    p[0] = LessExpression(p[1], p[3])

def p_expression_gt(p):
    'bool_expression : arith_expression GT arith_expression'
    p[0] = GreaterExpression(p[1], p[3])

def p_expression_le(p):
    'bool_expression : arith_expression LE arith_expression'
    p[0] = LessEqualExpression(p[1], p[3])

def p_expression_ge(p):
    'bool_expression : arith_expression GE arith_expression'
    p[0] = GreaterEqualExpression(p[1], p[3])

def p_expression_not(p):
    'bool_expression : NOT bool_expression'
    p[0] = NotExpression(p[2])

def p_expression_and(p):
    'bool_expression : bool_expression AND bool_expression'
    p[0] = AndExpression(p[1], p[3])

def p_expression_or(p):
    'bool_expression : bool_expression OR bool_expression'
    p[0] = OrExpression(p[1], p[3])

def p_expression_nand(p):
    'bool_expression : bool_expression NAND bool_expression'
    p[0] = NandExpression(p[1], p[3])

def p_expression_nor(p):
    'bool_expression : bool_expression NOR bool_expression'
    p[0] = NorExpression(p[1], p[3])

def p_expression_imp(p):
    'bool_expression : bool_expression IMP bool_expression'
    p[0] = ImpExpression(p[1], p[3])

parser = yacc(start='expression')
while True:
    print(parser.parse(input=input("> "), lexer=lexer).eval())