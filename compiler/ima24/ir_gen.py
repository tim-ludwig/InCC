from compiler.util import free_vars, make_unique_label
from syntaxtree.controlflow import IfExpression, LoopExpression, WhileExpression, DoWhileExpression
from syntaxtree.functions import CallExpression, LambdaExpression
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


def code_b(expr, env, kp):
    match expr:
        case SequenceExpression() | IfExpression() | WhileExpression() | DoWhileExpression() | LoopExpression() | LocalExpression():
            return code_c(expr, env, kp, code_b)

        case AssignExpression():
            return [
                *code_v(expr, env, kp),
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
                *code_b(expr, env, kp)
            ]

        case NumberLiteral(_, value):
            return [
                ('loadc', value),
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

        case VariableExpression():
            return [*code_v(expr, env, kp), ('getbasic',)]

        case _:
            raise NotImplementedError(expr)


def code_v(expr, env, kp):
    match expr:
        case SequenceExpression() | IfExpression() | WhileExpression() | DoWhileExpression() | LoopExpression() | LocalExpression():
            return code_c(expr, env, kp, code_v)

        case AssignExpression(_, var, expr):
            return [
                *code_v(var, env, kp),
                *code_v(expr, env, kp + 1),
                ('store',),
            ]

        case NumberLiteral() | UnaryOperatorExpression() | BinaryOperatorExpression():
            return [*code_b(expr, env, kp), ('mkbasic',), ('mkind', 'B'),]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'local':
            return [('pushloc', env[name]['address'])]

        case VariableExpression(_, name) if name in env and env[name]['scope'] == 'global':
            return [('pushglob', env[name]['address'])]

        case VariableExpression(_, name):
            raise KeyError(f'unknown variable {name}')


def code_c(expr, env, kp, code_x):
    match expr:
        case SequenceExpression(_, exprs):
            instructions = []
            for expr in exprs[:-1]:
                instructions += [
                    *code_b(expr, env, kp),
                    ('pop',),
                ]
            instructions += code_x(exprs[-1], env, kp)
            return instructions

        case IfExpression(_, condition, then_expr, else_expr):
            if_l, then_l, else_l, endif_l = make_unique_label('if', 'then', 'else', 'endif')
            return [
                ('label', if_l),
                *code_b(condition, env, kp),
                ('jumpz', else_l),
                ('label', then_l),
                *code_x(then_expr, env, kp),
                ('jump', endif_l),
                ('label', else_l),
                *code_x(else_expr, env, kp),
                ('label', endif_l),
            ]

        case WhileExpression(_, condition, body):
            while_l, endwhile_l = make_unique_label('while', 'end_while')
            return [
                ('loadc', 0),
                ('label', while_l),
                *code_b(condition, env, kp + 1),
                ('jumpz', endwhile_l),
                ('pop',),
                code_x(body, env, kp),
                ('jump', while_l),
                ('label', endwhile_l),
            ]

        case LoopExpression(_, count, body):
            loop_l, endloop_l = make_unique_label('loop', 'endloop')
            return [
                ('loadc', 0),
                *code_b(count, env, kp + 1),
                ('label', loop_l),
                ('dup',),
                ('jumpz', endloop_l),
                ('dec',),
                ('swap',),
                ('pop',),
                *code_x(body, env, kp + 1),
                ('swap',),
                ('jump', loop_l),
                ('label', endloop_l),
                ('pop',),
            ]

        case DoWhileExpression(_, condition, body):
            dowhile_l, enddowhile_l = make_unique_label('dowhile', 'enddowhile')
            return [
                ('label', dowhile_l),
                *code_x(body, env, kp),
                *code_b(condition, env, kp + 1),
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
                    *code_v(assignment, env2, kp + N),
                    ('pop',),
                ]

            return [
                *variables,
                *code_x(body, env2, kp + N),
                ('slide', N),
            ]

        case _:
            raise NotImplementedError(expr)