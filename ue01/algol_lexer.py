from ply import lex

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_COMMENT(t):
    r'comment[^;]*;'

def t_ID(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value,'ID')
    return t

def t_ASSIGN(t):
    r':='
    return t

def t_STRING(t):
    r'"(.*?(\")?)*"'
    t.value = t.value[1:-1] # remove "" around string
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s' in line %d" % (t.value[0], t.lineno))

reserved = {
    'begin' : 'BEGIN',
    'end' : 'END',
    'procedure' : 'PROCEDURE',
    'for' : 'FOR',
    'step' : 'STEP',
    'until' : 'UNTIL',
    'do' : 'DO',
}

literals = ';+-*/,()'
t_ignore = ' \t'

tokens = ['NUMBER', 'COMMENT', 'ID', 'ASSIGN', 'STRING'] + list(reserved.values())

lexer = lex.lex()

with open('factorial.alg', 'r') as f:
    lexer.input(f.read())

for token in lexer:
    print(token)