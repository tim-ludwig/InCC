from syntaxtree.variables import *


def p_expression_variable(p):
    """
    expression : IDENT
    """
    p[0] = VariableExpression(p.linespan(0), p[1])


def p_expression_assign(p):
    """
    expression : assign_expression
    assign_expression : IDENT ASSIGN expression
    """
    p[0] = p[1] if len(p) == 2 else AssignExpression(p.linespan(0), VariableExpression(p.linespan(1), p[1]), p[3])


def p_assignment_list(p):
    """
    assignment_list : assign_expression
                    | assign_expression COMMA assignment_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]


def p_lock(p):
    """
    expression : LOCK ident_list IN expression
    """
    p[0] = LockExpression(p.linespan(0), p[2], p[4])


def p_let(p):
    """
    expression : LOCAL assignment_list IN expression
    """
    p[0] = LocalExpression(p.linespan(0), p[2], p[4])
