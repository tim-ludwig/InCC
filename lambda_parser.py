from lambda_ast import *

def p_expression_lambda(p):
    'expression : IDENT RIGHT_ARROW expression'
    p[0] = LambdaExpression(p[1], p[3])

def p_expression_call(p):
    'expression : expression LPAREN expression RPAREN'
    p[0] = CallExpression(p[1], p[3])