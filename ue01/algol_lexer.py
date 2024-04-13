from ply import lex

def t_COMMENT(t):
    r'comment[^;]*;'

def t_STRING(t):
    r'"([^\n"]|\")*"'
    t.value = t.value[1:-1]
    return t

def t_NUMBER(t):
    r'-?(0x|0b)?[0-9][ _0-9]*'
    t.value = int(t.value)
    return t

reserved = {
    'begin' : 'BEGIN',
    'end' : 'END',
    'procedure' : 'PROCEDURE',
    'for' : 'FOR',
    'step' : 'STEP',
    'until' : 'UNTIL',
    'do' : 'DO',
}

def t_ID(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'ID')
    return t

def t_ASSIGN(t):
    r':='
    return t

def t_ANY_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s' in line %d" % (t.value[0], t.lineno))

literals = ';+-*/,()'
t_ignore = ' \t'

tokens = ['NUMBER', 'COMMENT', 'ID', 'ASSIGN', 'STRING'] + list(reserved.values())

lexer = lex.lex()

with open('factorial.alg', 'r') as f:
    lexer.input(f.read())

for token in lexer:
    print(token)