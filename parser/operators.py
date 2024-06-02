from syntaxtree.functions import CallExpression
from syntaxtree.variables import VariableExpression


def p_expression_binary(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression LT expression
               | expression GT expression
               | expression LE expression
               | expression GE expression
               | expression EQS expression
               | expression NEQS expression
               | expression EQ expression
               | expression NEQ expression
               | expression AND expression
               | expression OR expression
               | expression NAND expression
               | expression NOR expression
               | expression IMP expression
               | expression XOR expression
    """
    p[0] = CallExpression(VariableExpression(p[2]),  [p[1], p[3]])


def p_expression_unary(p):
    """
    expression : NOT expression
               | PLUS expression %prec UPLUS
               | MINUS expression %prec UMINUS
    """
    p[0] = CallExpression(VariableExpression(p[1]),  [p[2]])


def p_expression_access(p):
    """
    expression : expression LBRACKET expression RBRACKET
    """
    p[0] = CallExpression(VariableExpression('[]'), [p[1], p[3]])


def p_expression_paren(p):
    """
    expression : LPAREN expression RPAREN
    """
    p[0] = p[2]
