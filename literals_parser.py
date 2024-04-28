from literals_ast import *

def p_expression_num_lit(p):
    'expression : NUMBER'
    p[0] = NumberLiteral(p[1])

def p_expression_bool_lit(p):
    '''
    expression : TRUE
               | FALSE
    '''
    p[0] = BoolLiteral(p[1])