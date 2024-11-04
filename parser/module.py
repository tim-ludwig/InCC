from syntaxtree.module import ImportExpression


def p_module(p):
    """
    expression : IMPORT STRING
    """
    p[0] = ImportExpression(p[2])
