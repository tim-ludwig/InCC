from dataclasses import dataclass

import numpy as np

from lexer.lexer import make_incc24_lexer

from environment import Environment
from parser.parser import parse_expr, parse_file
from syntaxtree.controlflow import LoopExpression, WhileExpression, DoWhileExpression, IfExpression
from syntaxtree.literals import NumberLiteral, BoolLiteral, StringLiteral, CharLiteral, ArrayLiteral, DictLiteral
from syntaxtree.functions import LambdaExpression, CallExpression, ProcedureExpression
from syntaxtree.module import ImportExpression
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.struct import StructExpression, MemberAccessExpression, MemberAssignExpression, ThisExpression

from syntaxtree.syntaxtree import Expression, TrapExpression
from syntaxtree.variables import AssignExpression, VariableExpression, LockExpression, LocalExpression


@dataclass
class Closure:
    parent_env: Environment
    arg_names: list[str]
    body: Expression
    rest_args: bool
    local_names: list[str] = None

    def __call__(self, *arg_values):
        if self.local_names is None:
            env = self.parent_env.push(*self.arg_names)
        else:
            env = self.parent_env.push(*self.arg_names, *self.local_names)

        if self.rest_args:
            for i in range(len(self.arg_names) - 1):
                env[self.arg_names[i]] = arg_values[i]

            env[self.arg_names[-1]] = np.array(arg_values[len(self.arg_names) - 1:])
        else:
            for arg_name, arg_value in zip(self.arg_names, arg_values):
                env[arg_name] = arg_value

        return eval(self.body, env)

    def __str__(self):
        return f'fun(' + ', '.join(map(str, self.arg_names)) + ('...' if self.rest_args else '') + ')'

    def __repr__(self):
        return str(self)


def eval(expr: Expression, env: Environment):
    global dbg
    if dbg.should_stop(expr, env):
        dbg.debugger_stop(expr, env)

    match expr:
        case NumberLiteral(_, value): return float(value)
        case BoolLiteral(_, value): return value == 'TRUE'
        case StringLiteral(_, value): return value
        case CharLiteral(_, value): return value
        case ArrayLiteral(_, elements): return make_array(*[eval(elem, env) for elem in elements])
        case DictLiteral(_, elements): return {eval(key, env) : eval(value, env) for key, value in elements}

        case UnaryOperatorExpression(_, operator, operand):
            val = eval(operand, env)

            match operator:
                case '+': return +val
                case '-' : return -val
                case 'NOT': return not val

        case BinaryOperatorExpression(_, operator, operands):
            val0 = eval(operands[0], env)
            val1 = eval(operands[1], env)

            match operator:
                case '+': return val0 + val1
                case '-': return val0 - val1
                case '*': return val0 * val1
                case '/': return val0 / val1
                case '<': return val0 < val1
                case '>': return val0 > val1
                case '<=': return val0 <= val1
                case '>=': return val0 >= val1
                case '==': return val0 == val1
                case '!=': return val0 != val1
                case 'EQ': return val0 == val1
                case 'NEQ': return val0 != val1
                case 'XOR': return val0 != val1
                case 'AND': return val0 and val1
                case 'OR': return val0 or val1
                case 'NAND': return not (val0 and val1)
                case 'NOR': return not (val0 or val1)
                case 'IMP': return not val0 or val1
                case '[]':
                    if type(val0) != dict:
                        val1 = int(val1)
                    return val0[val1]

        case AssignExpression(_, var, expression):
            res = eval(expression, env)
            env[var.name] = res
            return res

        case VariableExpression(pos, name):
            if name not in env:
                raise KeyError(f"Unknown variable {name} in {pos[0]}:{pos[1]}")

            return env[name]

        case LockExpression(_, _, body):
            return eval(body, env)

        case LocalExpression(_, assignments, body):
            env = env.push(*[assignment.var.name for assignment in assignments])

            for assignment in assignments:
                eval(assignment, env)

            return eval(body, env)

        case SequenceExpression(_, expressions):
            result = None
            for expression in expressions:
                result = eval(expression, env)
            return result

        case LoopExpression(_, count, body):
            n = int(eval(count, env))

            result = None
            for _ in range(n):
                result = eval(body, env)
            return result

        case WhileExpression(_, condition, body):
            result = None
            while eval(condition, env):
                result = eval(body, env)
            return result

        case DoWhileExpression(_, condition, body):
            result = eval(body, env)
            while eval(condition, env):
                result = eval(body, env)
            return result

        case IfExpression(_, condition, then_body, else_body):
            if eval(condition, env):
                return eval(then_body, env)
            elif else_body:
                return eval(else_body, env)
            else:
                return None

        case LambdaExpression(_, arg_names, body, rest_args):
            return Closure(env, arg_names, body, rest_args)

        case ProcedureExpression(_, arg_names, local_names, body):
            return Closure(define_built_ins(env.root().push()), arg_names, body, False, local_names)

        case CallExpression(_, f, arg_exprs):
            callable = eval(f, env)
            arg_values = [eval(arg_expr, env) for arg_expr in arg_exprs]
            return callable(*arg_values)

        case StructExpression(_, initializers, parent_expr):
            if parent_expr:
                struct = eval(parent_expr, env).push()
            else:
                struct = Environment()

            struct.vars = {init_expr.name: None for init_expr in initializers}
            env = env.push()
            env.containing_struct = struct

            for init_expr in initializers:
                eval(init_expr, env)

            return struct

        case MemberAccessExpression(pos, expr, member, up_count):
            struct = eval(expr, env)

            for _ in range(up_count):
                struct = struct.parent

            if member not in struct:
                raise KeyError(f'Unknown member {member} in {pos[0]}:{pos[1]}')

            return struct[member]

        case MemberAssignExpression(pos, member, expr):
            if not env.containing_struct or member not in env.containing_struct.vars:
                raise KeyError(f'Unknown member {member} in {pos[0]}:{pos[1]}')

            val = eval(expr, env)
            env.containing_struct.vars[member] = val
            return val

        case ThisExpression(_):
            return env.containing_struct

        case ImportExpression(_, path):
            env = Environment()
            eval(parse_file(path), define_built_ins(env.push()))
            return env

        case TrapExpression(_):
            return None

        case _:
            raise NotImplementedError(expr)


class Debugger:
    def __init__(self):
        self.stepping = False
        self.stopped = False
        self.watching = {}

    def should_stop(self, expr, env):
        return not self.stopped and (type(expr) == TrapExpression or self.stepping)

    def debugger_stop(self, expr, env):
        self.stepping = True
        self.stopped = True

        while True:
            for text, e in self.watching.items():
                print(text, '=', eval(e, env))

            match input(f'{expr.position[0]} line {expr.position[1]}> ').split(' '):
                case ['s']:
                    break
                case ['c']:
                    self.stepping = False
                    break
                case ['v' | 'var' | 'vars']:
                    print('========== VAR DUMP ==========')
                    e = env
                    while e is not None:
                        for name, value in e.vars.items():
                            print(f'{name:<24} = {value}')
                        e = e.parent
                case ['w', *text]:
                    text = ' '.join(text)
                    self.watching[text] = parse_expr(text)
                case ['$' | 'e' | 'eval', *text]:
                    print(eval(parse_expr(' '.join(text)), env))

        self.stopped = False


def cons(a, b):
    return (a, b)


def make_list(*elem):
    if len(elem) == 0:
        return ()
    return cons(elem[0], make_list(*elem[1:]))


def head(l):
    return l[0]


def tail(l):
    return l[1]


def concat(a, b):
    return cons(head(a), concat(tail(a), b)) if a != () else b


def reverse(a):
    def rev(a, t):
        return rev(tail(a), cons(head(a), t)) if a != () else t
    return rev(a, ())


def list_map(f, l):
    return cons(f(head(l)), list_map(f, tail(l))) if l != () else ()


def make_array(*elem):
    return np.array(elem)


def define(env, name, val):
    env.vars[name] = val


def wrap_lexer(lexer):
    lexer_struct = Environment()

    def lexer_input(s):
        lexer.input(s)

    l = None
    def lexer_has_next():
        nonlocal l
        if l is None:
            l = lexer.token()

        return l is not None

    def lexer_next():
        nonlocal l
        t = l if l is not None else lexer.token()

        if t is None:
            return ()

        token_struct = Environment()
        define(token_struct, 'type', t.type)
        define(token_struct, 'value', t.value)
        define(token_struct, 'lineno', t.lineno)
        define(token_struct, 'lexpos', t.lexpos)
        return token_struct

    define(lexer_struct, 'input', lexer_input)
    define(lexer_struct, 'next', lexer_next)
    define(lexer_struct, 'has_next', lexer_has_next)

    return lexer_struct


def define_built_ins(env):
    define(env, 'list', make_list)
    define(env, 'cons', cons)
    define(env, 'nil', ())
    define(env, 'head', head)
    define(env, 'tail', tail)
    define(env, 'concat', concat)
    define(env, 'reverse', reverse)
    define(env, 'map', list_map)


    define(env, 'array', make_array)

    define(env, 'print', print)

    define(env, 'make_incc24_lexer', lambda: wrap_lexer(make_incc24_lexer()))

    return env


def main(args):
    global dbg
    global_vars = Environment()
    env = define_built_ins(global_vars.push())

    dbg = Debugger()
    if args.file:
        expr = parse_file(args.file)
        res = eval(expr, env)
        print(res)

    if args.repl:
        while True:
            try:
                inp = input("> ")
                expr = parse_expr(inp)
                res = eval(expr, env)
                print(res)
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                if args.stop_on_error:
                    raise e
                else:
                    print(e)
