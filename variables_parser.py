from variables_ast import *

def p_expression_variable(p):
    '''
    expression : IDENT
    '''
    p[0] = VariableRead(p[1])

def p_expression_assign_(p):
    '''
    expression : assign_expression
    '''
    p[0] = p[1]

def p_expression_assign(p):
    '''
    assign_expression : IDENT ASSIGN expression
    '''
    p[0] = VariableWrite(p[1], p[3])