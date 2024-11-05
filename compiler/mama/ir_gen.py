from syntaxtree.controlflow import IfExpression, WhileExpression, LoopExpression, DoWhileExpression
from syntaxtree.functions import ProcedureExpression, CallExpression
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.variables import AssignExpression, VariableExpression

unop_inst = {
    '-': ('neg',)
}
binop_inst = {
    '+': ('add',),
    '-': ('sub',),
    '*': ('mul',),
    '/': ('div',),
    '<':  ('le',),
    '>': ('gr',),
    '<=': ('leq',),
    '>=': ('geq',),
    '==': ('eq',),
    '!=': ('neq',),
}


label_count = dict()
def make_unique_label(*label):
    if len(label) > 1:
        return [make_unique_label(l) for l in label]

    label = label[0]

    global label_count
    label_count[label] = label_count.get(label, 0) + 1
    return label + str(label_count[label] - 1)


def code_b(expr, env, kp):
    match expr:
        case NumberLiteral(value):
            return [
                ('loadc', value)
            ]
        case UnaryOperatorExpression(operator, operand):
            return [
                *code_b(operand, env, kp),
                unop_inst[operator],
            ]
        case BinaryOperatorExpression(operator, operands):
            return [
                *code_b(operands[0], env, kp),
                *code_b(operands[1], env, kp + 1),
                binop_inst[operator],
            ]
        case IfExpression():
            return code_c(expr, env, kp, code_b)
        case None:
            return [
                ('loadc', 0),
            ]
        case _:
            raise NotImplementedError(expr)


def code_v(expr, env, kp):
    match expr:
        case NumberLiteral() | UnaryOperatorExpression() | BinaryOperatorExpression():
            return [*code_b(expr, env, kp), ('mkbasic',)]
        case IfExpression():
            return code_c(expr, env, kp, code_v)
        case None:
            return [
                ('loadc', 0),
            ]
        case _:
            raise NotImplementedError(expr)


def code_c(expr, env, kp, code_x):
    match expr:
        case IfExpression(condition, then_body, else_body):
            if_l, then_l, else_l, endif_l = make_unique_label('if', 'then', 'else', 'endif')
            return [
                ('label', if_l),
                *code_b(condition, env, kp),
                ('jumpz', else_l),
                ('label', then_l),
                *code_x(then_body, env, kp),
                ('jump', endif_l),
                ('label', else_l),
                *code_x(else_body, env, kp),
                ('label', endif_l),
            ]
        case _:
            raise NotImplementedError(expr)
