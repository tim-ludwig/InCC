from ply import lex

from lexer.literals import *
from lexer.operators import *
from lexer.struct import *
from lexer.variables import *
from lexer.sequences import *
from lexer.controlflow import *
from lexer.functions import *


reserved_words = set(
    lit_reserved_words
    | expr_reserved_words
    | var_reserved_words
    | controlflow_reserved_words
    | functions_reserved_words
    | struct_reserved_words
)
tokens = list(
    lit_tokens
    | expr_tokens
    | var_tokens
    | seq_tokens
    | functions_tokens
    | struct_tokens
    | reserved_words
)
tokens.extend(['IDENT', 'COMMA'])


t_COMMA = ','


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


def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}'")


def make_incc24_lexer():
    return lex.lex()


lexer = make_incc24_lexer()
