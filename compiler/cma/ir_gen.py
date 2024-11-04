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


start_addr = 0
def make_global(size):
    global start_addr
    start_addr += size
    return start_addr - size


label_count = dict()
def make_unique_label(*label):
    if len(label) > 1:
        return [make_unique_label(l) for l in label]

    label = label[0]

    global label_count
    label_count[label] = label_count.get(label, 0) + 1
    return label + str(label_count[label] - 1)


def code_r(expr, env):
    match expr:
        case NumberLiteral(value):
            return [
                ('loadc', value)
            ]
        case UnaryOperatorExpression(op, operand):
            return [
                *code_r(operand, env),
                unop_inst[op],
            ]
        case BinaryOperatorExpression(op, operands):
            return [
                *code_r(operands[0], env),
                *code_r(operands[1], env),
                binop_inst[op],
            ]
        case AssignExpression(VariableExpression(name) as var, expr):
            if name not in env:
                env[name].address = make_global(8)
                env[name].scope = 'global'
                env[name].size = 8

            return [
                *code_r(expr, env),
                *code_l(var, env),
                ('store',)
            ]
        case VariableExpression(name) as var:
            return [
                *code_l(var, env),
                ('load',)
            ]
        case SequenceExpression(exprs):
            instructions = []
            for expr in exprs[:-1]:
                instructions += code(expr, env)
            instructions += code_r(exprs[-1], env)
            return instructions
        case IfExpression(condition, then_expr, else_expr):
            if_l, then_l, else_l, endif_l = make_unique_label('if', 'then', 'else', 'endif')
            return [
                ('label', if_l),
                *code_r(condition, env),
                ('jumpz', else_l),
                ('label', then_l),
                *code_r(then_expr, env),
                ('jump', endif_l),
                ('label', else_l),
                *code_r(else_expr, env),
                ('label', endif_l),
            ]
        case WhileExpression(condition, body):
            while_l, endwhile_l = make_unique_label('while', 'end_while')
            return [
                ('loadc', 0),
                ('label', while_l),
                *code_r(condition, env),
                ('jumpz', endwhile_l),
                ('pop',),
                code_r(body, env),
                ('jump', while_l),
                ('label', endwhile_l),
            ]
        case LoopExpression(count, body):
            loop_l, endloop_l = make_unique_label('loop', 'endloop')
            return [
                ('loadc', 0),
                *code_r(count, env),
                ('label', loop_l),
                ('dup',),
                ('jumpz', endloop_l),
                ('dec',),
                ('swap',),
                ('pop',),
                *code_r(body, env),
                ('swap',),
                ('jump', loop_l),
                ('label', endloop_l),
                ('pop',),
            ]
        case DoWhileExpression(condition, body):
            dowhile_l, enddowhile_l = make_unique_label('dowhile', 'enddowhile')
            return [
                ('label', dowhile_l),
                *code_r(body, env),
                *code_r(condition, env),
                ('jumpz', enddowhile_l),
                ('jump', dowhile_l),
                ('label', enddowhile_l),
            ]
        case ProcedureExpression(arg_names, local_names, body):
            proc_l, endproc_l = make_unique_label('proc', 'endproc')

            env = env.root().push(*(arg_names + local_names))

            addr = -16
            for arg_name in arg_names:
                env[arg_name].scope = 'argument'
                env[arg_name].size = 8
                env[arg_name].address = addr
                addr -= 8

            addr = 8
            for local_name in local_names:
                env[local_name].scope = 'local'
                env[local_name].size = 8
                env[local_name].address = addr
                addr += 8

            return [
                ('jump', endproc_l),
                ('label', proc_l),

                ('enter',),
                ('alloc', sum([v.size for v in env.vars.values() if v.scope == 'local'])),
                *code_r(body, env),
                ('loadrc', -16),
                ('store',),
                ('pop',),
                ('ret',),

                ('label', endproc_l),
                ('loadc', proc_l),
            ]
        case CallExpression(f, arg_exprs):
            args = []
            for arg_expr in arg_exprs[::-1]:
                args += code_r(arg_expr, env)

            return [
                *args,
                ('mark',),
                *code_r(f, env),
                ('call',),
                ('pop',),
                ('slide', 8 * len(arg_exprs) - 8, 8),
            ]
        case None:
            return [
                ('loadc', 0),
            ]
        case _:
            raise NotImplementedError(expr)


def code(expr, env):
    return [*code_r(expr, env), ('pop',)]


def code_l(expr, env):
    match expr:
        case VariableExpression(name) if env[name].scope == 'global':
            return [
                ('loadc', env[name].address),
            ]
        case VariableExpression(name):
            return [
                ('loadrc', env[name].address),
            ]
        case _:
            raise NotImplementedError(expr)