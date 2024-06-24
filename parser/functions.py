from syntaxtree.functions import *
from syntaxtree.variables import AssignExpression, LocalExpression, VariableExpression


def p_ident_list(p):
    """
    ident_list : IDENT
               | IDENT COMMA ident_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]


def p_expression_lambda_(p):
    """
    expression : lambda_expression
    """
    p[0] = p[1]


def p_expression_lambda(p):
    """
    lambda_expression : BACKSLASH RIGHT_ARROW expression
                      | BACKSLASH ident_list RIGHT_ARROW expression
    """
    if len(p) == 5:
        p[0] = LambdaExpression(p[2], p[4])
    else:
        p[0] = LambdaExpression([], p[3])


def p_expression_lambda_rest_arg(p):
    """
    lambda_expression : BACKSLASH ident_list DOT DOT DOT RIGHT_ARROW expression
    """
    p[0] = LambdaExpression(p[2], p[7], True)


def p_expression_function(p):
    """
    expression : FUN IDENT lambda_expression
    """
    #    fun f x -> body
    # => f := local f := x -> body in f
    f_assign_lmbd = AssignExpression(p[2], p[3])
    p[0] = AssignExpression(p[2], LocalExpression(f_assign_lmbd, VariableExpression(p[2])))


def p_expr_list(p):
    """
    expr_list : expression
              | expression COMMA expr_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]


def p_expression_call(p):
    """
    expression : expression LPAREN expr_list RPAREN
               | expression LPAREN RPAREN
    """
    if len(p) == 4:
        p[0] = CallExpression(p[1], [])
    else:
        p[0] = CallExpression(p[1], p[3])
