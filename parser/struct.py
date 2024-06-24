from syntaxtree.struct import StructExpression, MemberAccessExpression


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


def p_struct_extension(p):
    """
    expression : EXTEND expression LBRACE RBRACE
               | EXTEND expression LBRACE initializer_list RBRACE
    """
    p[0] = StructExpression([] if len(p) == 5 else p[4], p[2])


def p_dots(p):
    """
    dots : DOT
         | DOT dots
    """
    if len(p) == 2:
        p[0] = 0
    else:
        p[0] = 1 + p[2]


def p_member_access(p):
    """
    expression : dots IDENT
               | expression dots IDENT
    """
    if len(p) == 3:
        p[0] = MemberAccessExpression(None, p[2], p[1])
    else:
        p[0] = MemberAccessExpression(p[1], p[3], p[2])
