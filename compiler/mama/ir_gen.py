from compiler.util import make_unique_label
from syntaxtree.controlflow import IfExpression
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.variables import LocalExpression, VariableExpression

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


def code_b(expr, env, kp):
    match expr:
        case IfExpression() | LocalExpression():
            return code_c(expr, env, kp, code_b)
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
        case VariableExpression():
            return [*code_v(expr, env, kp), ('getbasic',)]
        case None:
            return [
                ('loadc', 0),
            ]
        case _:
            raise NotImplementedError(expr)


def code_v(expr, env, kp):
    match expr:
        case IfExpression() | LocalExpression():
            return code_c(expr, env, kp, code_v)
        case NumberLiteral() | UnaryOperatorExpression() | BinaryOperatorExpression():
            return [*code_b(expr, env, kp), ('mkbasic',)]
        case VariableExpression(name) if name in env:
            return [('pushloc', env[name].addr)]
        case VariableExpression(name):
            raise KeyError(f'unknown variable {name}')
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
        case LocalExpression(assignments, body):
            env2 = env.push()

            variables = []
            N = len(assignments)
            for i in range(N):
                assignment = assignments[i]
                val = env2[assignment.var.name]
                val.scope = 'local'
                val.addr = kp + i + 1
                val.size = 1

                variables += code_v(assignment.expression, env, kp + i)

            return [
                *variables,
                *code_x(body, env2, kp + N),
                ('slide', N),
            ]
        case _:
            raise NotImplementedError(expr)
