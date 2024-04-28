from ply import lex
from operators_lexer import *

tokens = list(expr_tokens)
reserved_words = set(expr_reserved_words)

tokens.extend(reserved_words)

def t_IDENT(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'

    valUp = t.value.upper()
    if valUp in reserved_words:
        t.type = valUp
        t.value = valUp
    
    return t

t_ignore = ' \t\n'

lexer = lex.lex()