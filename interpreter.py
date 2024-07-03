import argparse
import sys
from dataclasses import dataclass
from typing import Self

import numpy as np

from parser import parser # type: ignore

from environment import Environment, Value
from parser.parser import parse_expr
from syntaxtree.controlflow import LoopExpression, WhileExpression, DoWhileExpression, IfExpression
from syntaxtree.literals import NumberLiteral, BoolLiteral, StringLiteral, CharLiteral, ArrayLiteral
from syntaxtree.functions import LambdaExpression, CallExpression
from syntaxtree.operators import OperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.struct import StructExpression, MemberAccessExpression, MemberAssignExpression, ThisExpression

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression, VariableExpression, LockExpression, LocalExpression


@dataclass
class Closure:
    parent_env: Environment
    arg_names: list[str]
    body: Expression
    rest_args: bool

    def __call__(self, *arg_values):
        env = self.parent_env.push(*self.arg_names)

        if self.rest_args:
            for i in range(len(self.arg_names) - 1):
                env[self.arg_names[i]].value = arg_values[i]

            env[self.arg_names[-1]].value = np.array(arg_values[len(self.arg_names) - 1:])
        else:
            for arg_name, arg_value in zip(self.arg_names, arg_values):
                env[arg_name].value = arg_value

        return eval(self.body, env)

    def __str__(self):
        return f'fun'


def eval(expr: Expression, env: Environment):
    match expr:
        case NumberLiteral(value): return float(value)
        case BoolLiteral(value): return value == 'TRUE'
        case StringLiteral(value): return value
        case CharLiteral(value): return value
        case ArrayLiteral(elements): return make_array(*[eval(elem, env) for elem in elements])

        case OperatorExpression(operator, operands):
            operand_values = [eval(operand_exp, env) for operand_exp in operands]
            return env[operator].value[len(operands)](*operand_values)

        case AssignExpression(name, expression):
            res = eval(expression, env)
            env[name].value = res
            return res

        case VariableExpression(name):
            if name not in env:
                raise KeyError(f"Unknown variable {name}")

            return env[name].value

        case LockExpression(_, body):
            return eval(body, env)

        case LocalExpression(assignments, body):
            env = env.push(*[assignment.name for assignment in assignments])

            for assignment in assignments:
                eval(assignment, env)

            return eval(body, env)

        case SequenceExpression(expressions):
            result = None
            for expression in expressions:
                result = eval(expression, env)
            return result

        case LoopExpression(count, body):
            n = int(eval(count, env))

            result = None
            for _ in range(n):
                result = eval(body, env)
            return result

        case WhileExpression(condition, body):
            result = None
            while eval(condition, env):
                result = eval(body, env)
            return result

        case DoWhileExpression(condition, body):
            result = eval(body, env)
            while eval(condition, env):
                result = eval(body, env)
            return result

        case IfExpression(condition, then_body, else_body):
            if eval(condition, env):
                return eval(then_body, env)
            elif else_body:
                return eval(else_body, env)
            else:
                return None

        case LambdaExpression(arg_names, body, rest_args):
            return Closure(env, arg_names, body, rest_args)

        case CallExpression(f, arg_exprs):
            callable = eval(f, env)
            arg_values = [eval(arg_expr, env) for arg_expr in arg_exprs]
            return callable(*arg_values)

        case StructExpression(initializers, parent_expr):
            if parent_expr:
                struct = eval(parent_expr, env).push()
            else:
                struct = Environment()

            struct.vars = {init_expr.name: Value() for init_expr in initializers}
            env = env.push()
            env.containing_struct = struct

            for init_expr in initializers:
                eval(init_expr, env)

            return struct

        case MemberAccessExpression(expr, member, up_count):
            struct = eval(expr, env)

            for _ in range(up_count):
                struct = struct.parent

            if member not in struct:
                raise KeyError(f'Unknown member {member}')

            return struct[member].value

        case MemberAssignExpression(member, expr):
            if not env.containing_struct or member not in env.containing_struct.vars:
                raise KeyError(f'Unknown member {member}')

            val = eval(expr, env)
            env.containing_struct.vars[member].value = val
            return val

        case ThisExpression():
            return env.containing_struct

        case _:
            raise NotImplementedError(expr)


def make_list(*elem):
    if len(elem) == 0:
        return ()
    return elem[0], make_list(*elem[1:])


def head(l):
    return l[0]


def tail(l):
    return l[1]


def make_array(*elem):
    return np.array(elem)


def define(env, name, val):
    env[name].value = val


def main(args):
    env = Environment()
    
    define(env, '+', {2: lambda v1, v2: v1 + v2, 1: lambda v: +v})
    define(env, '-', {2: lambda v1, v2: v1 - v2, 1: lambda v: -v})
    define(env, '*', {2: lambda v1, v2: v1 * v2})
    define(env, '/', {2: lambda v1, v2: v1 / v2})

    define(env, '<',  {2: lambda v1, v2: v1 < v2})
    define(env, '>',  {2: lambda v1, v2: v1 > v2})
    define(env, '<=', {2: lambda v1, v2: v1 <= v2})
    define(env, '>=', {2: lambda v1, v2: v1 >= v2})
    define(env, '=',  {2: lambda v1, v2: v1 == v2})
    define(env, '!=', {2: lambda v1, v2: v1 != v2})

    define(env, 'EQ',   {2: lambda v1, v2: v1 == v2})
    define(env, 'NEQ',  {2: lambda v1, v2: v1 != v2})
    define(env, 'XOR',  {2: lambda v1, v2: v1 != v2})
    define(env, 'AND',  {2: lambda v1, v2: v1 and v2})
    define(env, 'OR',   {2: lambda v1, v2: v1 or v2})
    define(env, 'NAND', {2: lambda v1, v2: not (v1 and v2)})
    define(env, 'NOR',  {2: lambda v1, v2: not (v1 or v2)})
    define(env, 'IMP',  {2: lambda v1, v2: not v1 or v2})
    define(env, 'NOT',  {1: lambda v1: not v1})

    define(env, 'list', make_list)
    define(env, 'cons', lambda v1, v2: (v1, v2))
    define(env, 'nil',  ())
    define(env, 'head', head)
    define(env, 'tail', tail)

    define(env, 'array', make_array)
    define(env, '[]',    {2: lambda v1, v2: v1[int(v2)]})

    define(env, 'print', lambda v: print(v))

    if args.file:
        with (open(args.file, 'r') as f):
            inp = f.read()
            print(inp)
            expr = parse_expr(inp)
            eval(expr, env)

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


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='interpreter', description='Run the interpreter')
    argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
    argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')
    argparser.add_argument('--stop-on-error', action='store_true', help='Stop the repl on error')

    args = argparser.parse_args()
    if args.stop_on_error and not args.repl:
        argparser.error('--stop-on-error requires --repl')

    main(args)
