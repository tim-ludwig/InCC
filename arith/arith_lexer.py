from ply.lex import lex
import re

t_ignore = ' \t\n'

tokens = [
    'NUMBER',
    'BOOL_LIT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LT', 'GT', 'LE', 'GE',
    'EQ', 'NEQ', 'BEQ', 'BNEQ',
    'NOT', 'AND', 'OR', 'NAND', 'NOR', 'IMP'
]

t_NUMBER='\d+(\.\d+)?'
t_BOOL_LIT='true|false'
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
t_EQ='='
t_NEQ='!='
t_BEQ='eq'
t_BNEQ='neq|xor'
t_NOT='not'
t_AND='and'
t_OR='or'
t_NAND='nand'
t_NOR='nor'
t_IMP='imp'

lexer = lex(reflags=re.IGNORECASE)