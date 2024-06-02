import argparse
from dataclasses import dataclass

import numpy as np

from parser import parser # type: ignore

from environment import Environment, Value
from parser.parser import parse_expr
from syntaxtree.controlflow import LoopExpression, WhileExpression, DoWhileExpression, IfExpression
from syntaxtree.literals import NumberLiteral, BoolLiteral, StringLiteral, CharLiteral, ArrayLiteral
from syntaxtree.functions import LambdaExpression, CallExpression
from syntaxtree.sequences import SequenceExpression

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression, VariableExpression, LockExpression, LocalExpression
from type_system.inference import generalise, infer_type
from type_system.parser import parse_type


@dataclass
class Closure:
    parent_env: Environment
    arg_names: list[str]
    body: Expression
    rest_args: bool

    def __call__(self, *arg_values):
        env = self.parent_env.push()
        env.create_local(*self.arg_names)

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

        case AssignExpression(name, expression):
            res = eval(expression, env)
            env[name].value = res
            return res

        case VariableExpression(name):
            return env[name].value

        case LockExpression(_, body):
            return eval(body, env)

        case LocalExpression(assignment, body):
            env = env.push()
            env.create_local(assignment.name)
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


def define(env, name, val, ty):
    env[name].value = val
    env[name].type = parse_type(ty)


def main(args):

    env = Environment()
    define(env, '+', lambda v1, v2: v1 + v2, 'number, number -> number')
    define(env, '-', lambda v1, v2: v1 - v2, 'number, number -> number')
    define(env, '*', lambda v1, v2: v1 * v2, 'number, number -> number')
    define(env, '/', lambda v1, v2: v1 / v2, 'number, number -> number')

    define(env, '<',  lambda v1, v2: v1 < v2,  'number, number -> bool')
    define(env, '>',  lambda v1, v2: v1 > v2,  'number, number -> bool')
    define(env, '<=', lambda v1, v2: v1 <= v2, 'number, number -> bool')
    define(env, '>=', lambda v1, v2: v1 >= v2, 'number, number -> bool')
    define(env, '=',  lambda v1, v2: v1 == v2, 'number, number -> bool')
    define(env, '!=', lambda v1, v2: v1 != v2, 'number, number -> bool')

    define(env, 'EQ',   lambda v1, v2: v1 == v2,        'bool, bool -> bool')
    define(env, 'NEQ',  lambda v1, v2: v1 != v2,        'bool, bool -> bool')
    define(env, 'XOR',  lambda v1, v2: v1 != v2,        'bool, bool -> bool')
    define(env, 'AND',  lambda v1, v2: v1 and v2,       'bool, bool -> bool')
    define(env, 'OR',   lambda v1, v2: v1 or v2,        'bool, bool -> bool')
    define(env, 'NAND', lambda v1, v2: not (v1 and v2), 'bool, bool -> bool')
    define(env, 'NOR',  lambda v1, v2: not (v1 or v2), 'bool, bool -> bool')
    define(env, 'IMP',  lambda v1, v2: not v1 or v2,   'bool, bool -> bool')
    define(env, 'NOT',  lambda v1: not v1,             'bool -> bool')

    define(env, 'list', make_list, 'a... -> list[a]')
    define(env, 'nil',  (),        'list[a]')
    define(env, 'head', head,      'list[a] -> a')
    define(env, 'tail', tail,      'list[a] -> list[a]')

    define(env, 'array', make_array,                 'a... -> array[a]')
    define(env, '[]',    lambda v1, v2: v1[int(v2)], 'array[a], number -> a')

    if args.file:
        with (open(args.file, 'r') as f):
            inp = f.read()
            expr = parse_expr(inp)
            infer_type(env, expr)
            eval(expr, env)

    if args.repl:
        while True:
            inp = input("> ")
            expr = parse_expr(inp)
            ty = infer_type(env, expr)
            res = eval(expr, env)
            print(f'{res} : {generalise(ty, env)}')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='interpreter', description='Run the interpreter')
    argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
    argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')

    main(argparser.parse_args())
