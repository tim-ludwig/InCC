expr_tokens = {
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LT', 'GT', 'LE', 'GE',
    'EQS', 'NEQS'
}
expr_reserved_words = {
    'EQ', 'NEQ', 'XOR', 'NOT', 'AND', 'OR', 'NAND', 'NOR', 'IMP'
}

t_PLUS=r'\+'
t_MINUS=r'-'
t_TIMES=r'\*'
t_DIVIDE=r'/'
t_LPAREN=r'\('
t_RPAREN=r'\)'
t_LT=r'<'
t_GT=r'>'
t_LE=r'<='
t_GE=r'>='
t_EQS=r'='
t_NEQS=r'!='