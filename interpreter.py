import argparse
from dataclasses import dataclass

from parser import parser # type: ignore

from environment import Environment, Value
from syntaxtree.controlflow import LoopExpression, WhileExpression, DoWhileExpression, IfExpression
from syntaxtree.literals import NumberLiteral, BoolLiteral
from syntaxtree.functions import LambdaExpression, CallExpression
from syntaxtree.sequences import SequenceExpression

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression, VariableExpression, LockExpression, LocalExpression
from type_inference.inference import unify, generalise, infer_type
from type_inference.types import TypeVar, TypeScheme, TypeFunc


@dataclass
class Closure:
    parent_env: Environment
    arg_names: list[str]
    body: Expression

    def __call__(self, *arg_values):
        env = self.parent_env.push()
        env.create_local(*self.arg_names)

        for arg_name, arg_value in zip(self.arg_names, arg_values):
            env[arg_name].value = arg_value

        return eval(self.body, env)

    def __str__(self):
        return f'fun'


def eval(expr: Expression, env: Environment):
    match expr:
        case NumberLiteral(value): return float(value)
        case BoolLiteral(value): return value == 'TRUE'

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

        case LambdaExpression(arg_names, body):
            return Closure(env, arg_names, body)

        case CallExpression(f, arg_exprs):
            callable = eval(f, env)
            arg_values = [eval(arg_expr, env) for arg_expr in arg_exprs]
            return callable(*arg_values)


def main(args):
    n = TypeFunc('Number', [])
    b = TypeFunc('Bool', [])
    any = TypeScheme('a', TypeVar('a'))
    nn_to_n = TypeFunc('->', [n, n, n])
    nn_to_b = TypeFunc('->', [n, n, b])
    bb_to_b = TypeFunc('->', [b, b, b])
    b_to_b = TypeFunc('->', [b, b])

    env = Environment()
    env.vars = {
        '+':    Value(lambda v1, v2: v1 + v2,         nn_to_n),
        '-':    Value(lambda v1, v2: v1 - v2,         nn_to_n),
        '*':    Value(lambda v1, v2: v1 * v2,         nn_to_n),
        '/':    Value(lambda v1, v2: v1 / v2,         nn_to_n),
        '<':    Value(lambda v1, v2: v1 < v2,         nn_to_b),
        '>':    Value(lambda v1, v2: v1 > v2,         nn_to_b),
        '<=':   Value(lambda v1, v2: v1 <= v2,        nn_to_b),
        '>=':   Value(lambda v1, v2: v1 >= v2,        nn_to_b),
        '=':    Value(lambda v1, v2: v1 == v2,        nn_to_b),
        '!=':   Value(lambda v1, v2: v1 != v2,        nn_to_b),
        'EQ':   Value(lambda v1, v2: v1 == v2,        bb_to_b),
        'NEQ':  Value(lambda v1, v2: v1 != v2,        bb_to_b),
        'XOR':  Value(lambda v1, v2: v1 != v2,        bb_to_b),
        'AND':  Value(lambda v1, v2: v1 and v2,       bb_to_b),
        'OR':   Value(lambda v1, v2: v1 or v2,        bb_to_b),
        'NAND': Value(lambda v1, v2: not (v1 and v2), bb_to_b),
        'NOR':  Value(lambda v1, v2: not (v1 or v2),  bb_to_b),
        'IMP':  Value(lambda v1, v2: not v1 or v2,    bb_to_b),
        'NOT':  Value(lambda v1:     not v1,          b_to_b),
    }

    if args.file:
        with (open(args.file, 'r') as f):
            inp = f.read()
            expr = parser.parse(inp)
            infer_type(env, expr)
            eval(expr, env)

    if args.repl:
        while True:
            inp = input("> ")
            expr = parser.parse(inp)
            ty = infer_type(env, expr)
            res = eval(expr, env)
            print(f'{res} : {generalise(ty, env)}')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='interpreter', description='Run the interpreter')
    argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
    argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')

    main(argparser.parse_args())
