from ply import lex

from lexer.literals import *
from lexer.operators import *
from lexer.variables import *
from lexer.sequences import *
from lexer.controlflow import *
from lexer.lmbd import *


tokens = list(
    lit_tokens
    | expr_tokens
    | var_tokens
    | seq_tokens
    | lambda_tokens
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
    """
    [_a-zA-Z][_a-zA-Z0-9]*
    """

    valUp = t.value.upper()
    if valUp in reserved_words:
        t.type = valUp
        t.value = valUp

    return t


def t_newline(t):
    r"""
    \n+
    """
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


lexer = lex.lex()
