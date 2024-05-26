from syntaxtree.lmbd import *


def p_ident_list(p):
    """
    ident_list :
               | IDENT
               | IDENT COMMA ident_list
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]


def p_expression_lambda(p):
    """
    expression : IDENT RIGHT_ARROW expression
               | LPAREN ident_list RPAREN RIGHT_ARROW expression
    """
    if len(p) == 4:
        p[0] = LambdaExpression([p[1]], p[3])
    else:
        p[0] = LambdaExpression(p[2], p[5])


def p_expr_list(p):
    """
    expr_list :
              | expression
              | expression COMMA expr_list
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]


def p_expression_call(p):
    """
    expression : expression LPAREN expr_list RPAREN
    """
    p[0] = CallExpression(p[1], p[3])
