from syntaxtree.module import ImportExpression


def p_module(p):
    """
    expression : IMPORT STRING
    """
    p[0] = ImportExpression(p.linespan(0), p[2])
