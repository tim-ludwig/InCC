import ast

lit_tokens = {
    'NUMBER', 'STRING', 'CHAR', 'LBRACKET', 'RBRACKET', 'COLON'
}
lit_reserved_words = {
    'TRUE', 'FALSE'
}

t_NUMBER = r'\d+(\.\d*)?|\.\d+'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'


def t_STRING(t):
    r'"(?:[^"\\]|\\.)*?"'
    t.value = ast.literal_eval(t.value)
    return t


def t_CHAR(t):
    r"'([^\n']|\')'"
    t.value = t.value[1:-1]
    return t
