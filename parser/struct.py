from syntaxtree.struct import StructExpression


def p_initializer_assign(p):
    """
    initializer : assign_expression
    """
    p[0] = p[1]


def p_initializer_list(p):
    """
    initializer_list : initializer
                     | initializer SEMICOLON initializer_list
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1], *p[3]]


def p_expr_struct(p):
    """
    expression : STRUCT LBRACE RBRACE
               | STRUCT LBRACE initializer_list RBRACE
    """
    p[0] = StructExpression([] if len(p) == 4 else p[3])