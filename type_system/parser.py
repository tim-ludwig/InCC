from ply import lex, yacc

from environment import Environment
from type_system.inference import generalise
from type_system.types import TypeFunc, TypeVar

tokens = ['IDENT', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'RARROW', 'COMMA', 'TYPE_NAME']
known_types = {
    'number',
    'bool',
}

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_RARROW = r'->'
t_COMMA = r','

t_ignore = ' \t\n'


def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'

    valLow = t.value.lower()
    if valLow in known_types:
        t.type = 'TYPE_NAME'
        t.value = valLow

    return t


precedence = [
    ['right', 'RARROW'],
    ['left', 'COMMA'],
]


def p_type_list(p):
    """
    type_list : type
              | type COMMA type_list
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1], *p[3]]


def p_type_func(p):
    """
    type : IDENT LBRACKET type_list RBRACKET
         | IDENT LBRACKET RBRACKET
         | TYPE_NAME
    """
    p[0] = TypeFunc(p[1], p[3]) if len(p) == 5 else TypeFunc(p[1], [])


def p_func_type_func(p):
    """
    type : type_list RARROW type
    """
    p[0] = TypeFunc('->', [*p[1], p[3]])


def p_paren(p):
    """
    type : LPAREN type RPAREN
    """
    p[0] = p[2]


def p_type_var(p):
    """
    type : IDENT
    """
    p[0] = TypeVar(p[1])


lexer = lex.lex()
type_parser = yacc.yacc(start='type')


def parse_type(text: str):
    return generalise(type_parser.parse(input=text, lexer=lexer), Environment())
