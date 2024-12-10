from compiler.util import free_vars, make_unique_label
from syntaxtree.controlflow import IfExpression, LoopExpression, WhileExpression, DoWhileExpression, RepeatExpression
from syntaxtree.functions import CallExpression, LambdaExpression, ReturnExpression, QuitExpression
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.syntaxtree import Program
from syntaxtree.variables import VariableExpression, AssignExpression, LocalExpression

unop_inst = {
    '-': ('neg',),
}
binop_inst = {
    '+':  ('add',),
    '-':  ('sub',),
    '*':  ('mul',),
    '/':  ('div',),
    '<':  ('le',),
    '>':  ('gr',),
    '<=': ('leq',),
    '>=': ('geq',),
    '==': ('eq',),
    '!=': ('neq',),
}


def code_b(expr, env, kp, info):
    match expr:
        case SequenceExpression() | IfExpression() | WhileExpression() | DoWhileExpression() | LoopExpression() | LocalExpression():
            return code_c(expr, env, kp, info, code_b)

        case VariableExpression() | AssignExpression() | CallExpression() | RepeatExpression():
            return [
                *code_v(expr, env, kp, info),
                ('getbasic',),
            ]

        case Program(_, expr):
            global_vars = list(free_vars(expr))
            n = len(global_vars)

            for i in range(n):
                env[global_vars[i]] = {'scope': 'global', 'address': i}

            return [
                ('alloc', n),
                ('mkvec', n),
                ('setgp',),
                *code_b(expr, env, kp, info)
            ]

        case NumberLiteral(_, value):
            return [
                ('loadc', value),
            ]

        case UnaryOperatorExpression(_, operator, operand):
            return [
                *code_b(operand, env, kp, info),
                unop_inst[operator],
            ]

        case BinaryOperatorExpression(_, operator, operands):
            return [
                *code_b(operands[0], env, kp, info),
                *code_b(operands[1], env, kp + 1, info),
                binop_inst[operator],
            ]

        case _:
            raise NotImplementedError(expr)


def code_v(expr, env, kp, info):
    match expr:
        case SequenceExpression() | IfExpression() | WhileExpression() | DoWhileExpression() | LoopExpression() | LocalExpression():
            return code_c(expr, env, kp, info, code_v)

        case AssignExpression(_, var, expr):
            return [
                *code_v(var, env, kp, info),
                *code_v(expr, env, kp + 1, info),
                ('store',),
            ]

        case NumberLiteral() | UnaryOperatorExpression() | BinaryOperatorExpression():
            return [*code_b(expr, env, kp, info), ('mkbasic',), ('mkind', 'B'), ]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'local':
            return [('pushloc', env[name]['address'])]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'global':
            return [('pushglob', env[name]['address'])]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'formal':
            return [('pushform', env[name]['address'])]

        case VariableExpression(_, name):
            raise KeyError(f'unknown variable {name}')

        case LambdaExpression(_, arg_names, body, _):
            fun_l = make_unique_label('fun')
            free_v = list(free_vars(expr))
            free_v_code = []
            m = len(free_v)

            env2 = env.push(*arg_names, *free_v)
            for i in range(m):
                free_v_code += code_v(VariableExpression(None, free_v[i]), env, kp + i, info)
                env2[free_v[i]] = {'scope': 'global', 'address': i}

            for i in range(len(arg_names)):
                env2[arg_names[i]] = {'scope': 'formal', 'address': i}

            body_inst = [
                ('label', fun_l),
                *code_v(body, env2, 0, info),
                ('return', 0),
            ]

            info['lb'][fun_l] = body_inst

            return [
                *free_v_code,
                ('mkvec', m),
                ('mkfunval', fun_l),
                ('mkind', 'F'),
            ]

        case CallExpression(_, f, arg_exprs):
            ret_l = make_unique_label('ret')
            m = len(arg_exprs)
            args = []

            for i in range(m):
                args += code_v(arg_exprs[i], env, kp + 1 + i, info)

            if 'quit_addr' in info:
                retv = [
                    ('loadc', ret_l),
                    ('loadc', info['quit_addr']),
                    ('mkvec', 2),
                ]
            else:
                retv = [
                    ('loadc', ret_l),
                    ('mkvec', 1),
                ]

            return [
                *code_v(f, env, kp, info),
                *args,
                ('mkvec', m),
                *retv,
                ('call',),
                ('label', ret_l),
            ]

        case RepeatExpression(_, body):
            repeat_l, quitrepeat_l = make_unique_label('repeat', 'quitrepeat')
            info2 = dict(info)
            info2['quit_addr'] = quitrepeat_l

            return [
                ('label', repeat_l),
                *code_v(body, env, kp, info2),
                ('jump', repeat_l),
                ('label', quitrepeat_l),
                ('cleansp', kp)
            ]

        case ReturnExpression(_, val):
            return [
                *code_v(val, env, kp, info),
                ('return', 0),
            ]

        case QuitExpression(_, val):
            return [
                *code_v(val, env, kp, info),
                ('return', 1),
            ]

        case None:
            return [('loadc', 0)]

        case _:
            raise NotImplementedError(expr)


def code_c(expr, env, kp, info, code_x):
    match expr:
        case SequenceExpression(_, exprs):
            instructions = []
            for expr in exprs[:-1]:
                instructions += [
                    *code_x(expr, env, kp, info),
                    ('pop',),
                ]
            instructions += code_x(exprs[-1], env, kp, info)
            return instructions

        case IfExpression(_, condition, then_expr, else_expr):
            if_l, then_l, else_l, endif_l = make_unique_label('if', 'then', 'else', 'endif')
            return [
                ('label', if_l),
                *code_b(condition, env, kp, info),
                ('jumpz', else_l),
                ('label', then_l),
                *code_x(then_expr, env, kp, info),
                ('jump', endif_l),
                ('label', else_l),
                *code_x(else_expr, env, kp, info),
                ('label', endif_l),
            ]

        case WhileExpression(_, condition, body):
            while_l, endwhile_l = make_unique_label('while', 'end_while')
            return [
                ('loadc', 0),
                ('label', while_l),
                *code_b(condition, env, kp + 1, info),
                ('jumpz', endwhile_l),
                ('pop',),
                code_x(body, env, kp, info),
                ('jump', while_l),
                ('label', endwhile_l),
            ]

        case LoopExpression(_, count, body):
            loop_l, endloop_l = make_unique_label('loop', 'endloop')
            return [
                ('loadc', 0),
                *code_b(count, env, kp + 1, info),
                ('label', loop_l),
                ('dup',),
                ('jumpz', endloop_l),
                ('dec',),
                ('swap',),
                ('pop',),
                *code_x(body, env, kp + 1, info),
                ('swap',),
                ('jump', loop_l),
                ('label', endloop_l),
                ('pop',),
            ]

        case DoWhileExpression(_, condition, body):
            dowhile_l, enddowhile_l = make_unique_label('dowhile', 'enddowhile')
            return [
                ('label', dowhile_l),
                *code_x(body, env, kp, info),
                *code_b(condition, env, kp + 1, info),
                ('jumpz', enddowhile_l),
                ('pop',),
                ('jump', dowhile_l),
                ('label', enddowhile_l),
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
                    *code_v(assignment, env2, kp + N, info),
                    ('pop',),
                ]

            return [
                *variables,
                *code_x(body, env2, kp + N, info),
                ('slide', N),
            ]

        case _:
            raise NotImplementedError(expr)