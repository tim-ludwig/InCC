from variables_ast import *

def p_expression_variable(p):
    '''
    expression : IDENT
    '''
    p[0] = VariableRead(p[1])

def p_expression_assign(p):
    '''
    expression : assign_expression
    assign_expression : IDENT ASSIGN expression
    '''
    p[0] = p[1] if len(p) == 2 else VariableWrite(p[1], p[3])

def p_ident_list(p):
    '''
    ident_list : IDENT
               | ident_list COMMA IDENT
    '''
    p[0] = [p[1]] if len(p) == 2 else [*p[1], p[3]]

def p_lock(p):
    '''
    expression : LOCK ident_list expression
    '''
    p[0] = VariableLock(p[2], p[3])