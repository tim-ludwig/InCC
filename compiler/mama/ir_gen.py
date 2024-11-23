from compiler.util import make_unique_label
from syntaxtree.controlflow import IfExpression
from syntaxtree.functions import CallExpression, LambdaExpression
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.variables import LocalExpression, VariableExpression, AssignExpression

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


def free_vars(expr):
    match expr:
        case NumberLiteral(_, _):
            return set()

        case UnaryOperatorExpression(_, _, operand):
            return free_vars(operand)

        case BinaryOperatorExpression(_, _, (left, right)):
            return free_vars(left) | free_vars(right)

        case AssignExpression(_, var, expression):
            return  free_vars(var) | free_vars(expression)

        case VariableExpression(_, name):
            return {name}

        case IfExpression(_, condition, then_body, else_body):
            return free_vars(condition) | free_vars(then_body) | free_vars(else_body)

        case LocalExpression(_, assignments, body):
            return free_vars(body) - {assignment.var.name for assignment in assignments}

        case LambdaExpression(_, arg_names, body, _):
            return free_vars(body) - set(arg_names)

        case CallExpression(_, f, args):
            return free_vars(f) | {v for arg in args for v in free_vars(arg)}

        case _:
            raise NotImplementedError(expr)

def code_b(expr, env, kp):
    match expr:
        case IfExpression() | LocalExpression():
            return code_c(expr, env, kp, code_b)

        case NumberLiteral(_, value):
            return [
                ('loadc', value)
            ]

        case UnaryOperatorExpression(_, operator, operand):
            return [
                *code_b(operand, env, kp),
                unop_inst[operator],
            ]

        case BinaryOperatorExpression(_, operator, operands):
            return [
                *code_b(operands[0], env, kp),
                *code_b(operands[1], env, kp + 1),
                binop_inst[operator],
            ]

        case VariableExpression() | CallExpression():
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

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'local':
            return [('pushloc', kp - env[name]['address'])]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'global':
            return [('pushglob', env[name]['address'])]

        case VariableExpression(_, name):
            raise KeyError(f'unknown variable {name}')

        case CallExpression(_, f, arg_exprs):
            ret_l = make_unique_label('ret')
            m = len(arg_exprs)
            args = []

            for i in range(m):
                args += code_v(arg_exprs[m - 1 - i], env, kp + 3 + i)

            return [
                ('mark', ret_l),
                *args,
                *code_v(f, env, kp + 3 + m),
                ('apply',),
                ('label', ret_l),
            ]

        case LambdaExpression(_, arg_names, body, _):
            fun_l, after_l = make_unique_label('fun', 'after')
            free_v = list(free_vars(expr))
            free_v_code = []
            m = len(free_v)

            env2 = env.push(*arg_names, *free_v)
            for i in range(m):
                free_v_code += code_v(VariableExpression(None, free_v[i]), env, kp + i)
                env2[free_v[i]] = {'scope': 'global', 'address': i}

            for i in range(len(arg_names)):
                env2[arg_names[i]] = {'scope': 'local', 'address': -i}

            return [
                *free_v_code,
                ('mkvec', m),
                ('mkfunval', fun_l),
                ('jump', after_l),
                ('label', fun_l),
                *code_v(body, env2, 0),
                ('popenv',),
                ('label', after_l),
            ]

        case None:
            return [
                ('loadc', 0),
            ]

        case _:
            raise NotImplementedError(expr)


def code_c(expr, env, kp, code_x):
    match expr:
        case IfExpression(_, condition, then_body, else_body):
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

        case LocalExpression(_, assignments, body):
            env2 = env.push(*[assignment.var.name for assignment in assignments])

            N = len(assignments)
            for i in range(N):
                assignment = assignments[i]
                env2[assignment.var.name] = {'scope': 'local', 'address': kp + i + 1}

            variables = [('alloc', N)]
            for i in range(N):
                assignment = assignments[i]
                variables += [
                    *code_v(assignment.expression, env2, kp + N),
                    ('rewrite', N - i),
                ]

            return [
                *variables,
                *code_x(body, env2, kp + N),
                ('slide', N),
            ]

        case _:
            raise NotImplementedError(expr)
