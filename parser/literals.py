from syntaxtree.literals import *


def p_expression_num_lit(p):
    """
    expression : NUMBER
    """
    p[0] = NumberLiteral(p.linespan(0), p[1])


def p_expression_bool_lit(p):
    """
    expression : TRUE
               | FALSE
    """
    p[0] = BoolLiteral(p.linespan(0), p[1])


def p_expression_str_lit(p):
    """
    expression : STRING
    """
    p[0] = StringLiteral(p.linespan(0), p[1])


def p_expression_char_lit(p):
    """
    expression : CHAR
    """
    p[0] = CharLiteral(p.linespan(0), p[1])


def p_expression_array_lit(p):
    """
    expression : LBRACKET RBRACKET
               | LBRACKET expr_list RBRACKET
    """
    p[0] = ArrayLiteral(p.linespan(0), []) if len(p) == 3 else ArrayLiteral(p.linespan(0), p[2])
