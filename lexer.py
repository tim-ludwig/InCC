from ply import lex

from literals_lexer import *
from operators_lexer import *
from variables_lexer import *
from sequences_lexer import *
from controlflow_lexer import *

tokens = list(
    lit_tokens
  | expr_tokens
  | var_tokens
  | seq_tokens
)
reserved_words = set(
    lit_reserved_words
  | expr_reserved_words
  | var_reserved_words
  | controlflow_reserved_words
)

tokens.extend(reserved_words)

tokens.append('IDENT')
def t_IDENT(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'

    valUp = t.value.upper()
    if valUp in reserved_words:
        t.type = valUp
        t.value = valUp
    
    return t

t_ignore = ' \t\n'
t_ignore_COMMENT = r'\#.*'

lexer = lex.lex()