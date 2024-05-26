import argparse
from parser import parser # type: ignore

from environment import Environment, Value
from syntaxtree.controlflow import LoopExpression, ForExpression, WhileExpression, DoWhileExpression, IfExpression
from syntaxtree.literals import NumberLiteral, BoolLiteral
from syntaxtree.lmbd import LambdaExpression, CallExpression, Closure
from syntaxtree.operators import OperatorExpression
from syntaxtree.sequences import SequenceExpression

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression, VariableExpression, LockExpression, LocalExpression


def eval(expr: Expression, env: Environment):
    match expr:
        case NumberLiteral(value): return float(value)
        case BoolLiteral(value): return bool(value)

        case OperatorExpression(op, operands):
            return OperatorExpression.operators[op][len(operands)](*[eval(operand, env) for operand in operands])

        case AssignExpression(name, expression):
            res = eval(expression, env)
            env[name] = Value(res)
            return res

        case VariableExpression(name):
            return env[name].value

        case LockExpression(_, body):
            return eval(body, env)

        case LocalExpression(assignment, body):
            env = env.push()
            env.define_local(assignment.name, Value(None))
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

        case ForExpression(initial_assign, condition, reassign, body):
            eval(initial_assign, env)

            result = None
            while eval(condition, env):
                result = eval(body, env)
                eval(reassign, env)
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

        case CallExpression(lmbd, args):
            closure = eval(lmbd, env)

            cenv = closure.env.push()
            for arg_name, arg_expr in zip(closure.arg_names, args):
                cenv.define_local(arg_name, Value(eval(arg_expr, env)))
            return eval(closure.body, cenv)


def main(args):
    env = Environment()

    if args.file:
        with (open(args.file, 'r') as f):
            inp = f.read()
            expr = parser.parse(inp)
            res = eval(expr, env)
            print(res)

    if args.repl:
        while True:
            inp = input("> ")
            expr = parser.parse(inp)
            res = eval(expr, env)
            print(res)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog='interpreter', description='Run the interpreter')
    argparser.add_argument('file', type=str, nargs='?', help='The file to interpret')
    argparser.add_argument('--repl', action='store_true', help='Run the interpreter in REPL mode')

    main(argparser.parse_args())
