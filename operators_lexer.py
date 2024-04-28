expr_tokens = {
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LT', 'GT', 'LE', 'GE',
    'EQS', 'NEQS'
}
expr_reserved_words = {
    'EQ', 'NEQ', 'XOR', 'NOT', 'AND', 'OR', 'NAND', 'NOR', 'IMP'
}

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