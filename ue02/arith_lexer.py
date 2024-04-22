from ply.lex import lex
import re

t_ignore = ' \t\n'

tokens = [
    'NUMBER',
    'IDENT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LT', 'GT', 'LE', 'GE',
    'EQS', 'NEQS'
]
reseved_words = {
    'TRUE', 'FALSE', 'EQ', 'NEQ', 'XOR', 'NOT', 'AND', 'OR', 'NAND', 'NOR', 'IMP'
}
tokens.extend(reseved_words)

t_NUMBER='\d+(\.\d+)?'
t_PLUS='\+'
t_MINUS='-'
t_TIMES='\*'
t_DIVIDE='/'
t_LPAREN='\('
t_RPAREN='\)'
t_LT='<'
t_GT='>'
t_LE='<='
t_GE='>='
t_EQS='='
t_NEQS='!='

def t_IDENT(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'

    valUp = t.value.upper()
    if valUp in reseved_words:
        t.type = valUp
        t.value = valUp
    
    return t

lexer = lex()