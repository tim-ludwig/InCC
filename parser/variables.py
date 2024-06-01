from syntaxtree.variables import *


def p_expression_variable(p):
    """
    expression : IDENT
    """
    p[0] = VariableExpression(p[1])


def p_expression_assign(p):
    """
    expression : assign_expression
    assign_expression : IDENT ASSIGN expression
    """
    p[0] = p[1] if len(p) == 2 else AssignExpression(p[1], p[3])


def p_lock(p):
    """
    expression : LOCK IDENT IN expression
    """
    p[0] = LockExpression(p[2], p[4])


def p_let(p):
    """
    expression : LOCAL assign_expression IN expression
    """
    p[0] = LocalExpression(p[2], p[4])
