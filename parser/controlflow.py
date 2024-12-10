from syntaxtree.controlflow import *
from syntaxtree.sequences import SequenceExpression


def p_loop(p):
    """
    expression : LOOP expression DO expression
    """
    p[0] = LoopExpression(p.linespan(0), p[2], p[4])


def p_for(p):
    """
    expression : FOR assign_expression SEMICOLON expression SEMICOLON assign_expression DO expression
    """
    p[0] = SequenceExpression(p.linespan(0), [p[2], WhileExpression(p[4], SequenceExpression([p[8], p[6]]))])


def p_while(p):
    """
    expression : WHILE expression DO expression
    """
    p[0] = WhileExpression(p.linespan(0), p[2], p[4])


def p_do_while(p):
    """
    expression : DO expression WHILE expression
    """
    p[0] = DoWhileExpression(p.linespan(0), p[4], p[2])


def p_if(p):
    """
    expression : IF expression THEN expression
               | IF expression THEN expression ELSE expression
    """
    p[0] = IfExpression(p.linespan(0), p[2], p[4], p[6] if len(p) == 7 else None)


def p_repeat(p):
    """
    expression : REPEAT expression
    """
    p[0] = RepeatExpression(p.linespan(0), p[2])
