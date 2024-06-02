from unittest import case

from environment import Environment, Value
from syntaxtree.controlflow import IfExpression, LoopExpression, WhileExpression, DoWhileExpression
from syntaxtree.functions import LambdaExpression, CallExpression
from syntaxtree.literals import BoolLiteral, NumberLiteral, StringLiteral, CharLiteral, ArrayLiteral
from syntaxtree.sequences import SequenceExpression
from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import VariableExpression, AssignExpression, LocalExpression, LockExpression
from type_system.substitution import Substitution
from type_system.types import Type, MonoType, TypeScheme, TypeVar, TypeFunc, FunctionType


def instantiate(ty: Type) -> MonoType:
    match ty:
        case MonoType():
            return ty

        case TypeScheme(bound_vars, t):
            s = Substitution({bound_var: TypeVar.new() for bound_var in bound_vars})
            return s(t)


def generalise(ty: Type, env: Environment) -> Type:
    fv = ty.free_vars() - env.free_type_vars()
    if len(fv) == 0:
        return ty

    renaming = {old: chr(new) for new, old in enumerate(fv, start=ord('a'))}

    s = Substitution({v: TypeVar(renaming[v]) for v in fv})
    return TypeScheme(list(renaming.values()), s(ty))


def unify(t1: MonoType, t2: MonoType, hint: str = '') -> Substitution:
    match t1:
        case TypeVar(name1):
            match t2:
                case TypeVar(name2):
                    if name1 == name2:
                        return Substitution({})
                    else:
                        return Substitution({name2: t1})

                case TypeFunc() | FunctionType():
                    if name1 in t2.free_vars():
                        raise TypeError('Infinite type on unify')
                    return Substitution({name1: t2})

        case TypeFunc(name1, args1):
            match t2:
                case TypeVar():
                    return unify(t2, t1, hint)

                case TypeFunc(name2, args2):
                    if name1 == name2 and len(args1) == len(args2):
                        s = Substitution({})

                        for arg1, arg2 in zip(args1, args2):
                            s = unify(s(arg1), s(arg2), hint)(s)

                        return s

        case FunctionType(ret1, args1, rest_arg1):
            match t2:
                case TypeVar():
                    return unify(t2, t1, hint)

                case FunctionType(ret2, args2, rest_arg2):
                    if rest_arg1 == rest_arg2 and len(args1) == len(args2):
                        s = unify(ret1, ret2, hint)

                        for arg1, arg2 in zip(args1, args2):
                            s = unify(s(arg1), s(arg2), hint)(s)

                        return s

                    if rest_arg1 and len(args1) - 1 <= len(args2):
                        s = unify(ret1, ret2, hint)
                        for i in range(len(args1) - 1):
                            s = unify(s(args1[i]), s(args2[i]), hint)(s)

                        for i in range(len(args1) - 1, len(args2)):
                            s = unify(s(args1[-1]), s(args2[i]), hint)(s)

                        return s

                    if rest_arg2:
                        unify(t2, t1, hint)

    raise TypeError(f"Types '{t1}' and '{t2}' don't match.\n\tHint: {hint}")


def infer_type(env: Environment, expr: Expression) -> Type:
    s, t = algorithm_w(env, expr)
    return t


def algorithm_w(env: Environment, expr: Expression) -> (Substitution, Type):
    s, t = _algorithm_w(env, expr)
    expr.type = t
    return s, t


def _algorithm_w(env: Environment, expr: Expression) -> (Substitution, Type):
    match expr:
        case NumberLiteral(value): return Substitution({}), TypeFunc('number', [])
        case BoolLiteral(value): return Substitution({}), TypeFunc('bool', [])
        case StringLiteral(value): return Substitution({}), TypeFunc('string', [])
        case CharLiteral(value): return Substitution({}), TypeFunc('char', [])

        case ArrayLiteral(elements):
            elem_type = TypeVar.new()
            s = Substitution({})
            for elem in elements:
                s_new, t = algorithm_w(env, elem)
                s_new(env)
                s = s_new(s)

                s_new = unify(s(elem_type), s(t), 'Array elements have to be the same type')
                s_new(env)
                s = s_new(s)

            return s, s(TypeFunc('array', [elem_type]))

        case AssignExpression(name, expression):
            s, t = algorithm_w(env, expression)
            s(env)

            if name in env:
                s_new = unify(env[name].type, t, "can't change type of variable")
                s = s_new(s)

            env[name].type = generalise(t, env)

            return s, s(t)

        case VariableExpression(name):
            return Substitution({}), instantiate(env[name].type)

        case LockExpression(name, body): return algorithm_w(env, body)

        case LocalExpression(assignment, body):
            env = env.push()
            env[assignment.name].type = TypeVar.new()
            s, _ = algorithm_w(env, assignment)
            s(env)

            s_new, t = algorithm_w(env, body)
            s_new(env)
            s = s_new(s)
            return s, s(t)

        case SequenceExpression(expressions):
            s = Substitution({})
            t = TypeFunc('()', [])

            for expr in expressions:
                s_new, t = algorithm_w(env, expr)
                s_new(env)
                s = s_new(s)

            return s, s(t)

        case LoopExpression(count, body):
            s, count_type = algorithm_w(env, count)
            s(env)

            s_new = unify(count_type, TypeFunc('number', []), f"count of loop hast to have type number, has type {count_type}")
            s_new(env)
            s = s_new(s)

            s_new, t = algorithm_w(env, body)
            s_new(env)
            s = s_new(s)
            return s, s(t)

        case WhileExpression(condition, body):
            s, cond_type = algorithm_w(env, condition)
            s(env)

            s_new = unify(cond_type, TypeFunc('bool', []), f"condition of while hast to have type bool, has type {cond_type}")
            s_new(env)
            s = s_new(s)

            s_new, t = algorithm_w(env, body)
            s_new(env)
            s = s_new(s)
            return s, s(t)

        case DoWhileExpression(condition, body):
            s, t = algorithm_w(env, body)
            s(env)

            s_new, cond_type = algorithm_w(env, condition)
            s_new(env)
            s = s_new(s)

            s_new = unify(cond_type, TypeFunc('bool', []), f"condition of do-while hast to have type bool, has type {cond_type}")
            s_new(env)
            s = s_new(s)

            return s, s(t)

        case IfExpression(condition, then_body, else_body):
            s, cond_type = algorithm_w(env, condition)
            s(env)

            s_new = unify(cond_type, TypeFunc('bool', []), f"condition of if hast to have type bool, has type {cond_type}")
            s_new(env)
            s = s_new(s)

            s_new, then_type = algorithm_w(env, then_body)
            s_new(env)
            s = s_new(s)

            s_new, else_type = algorithm_w(env, else_body)
            s_new(env)
            s = s_new(s)

            s_new = unify(then_type, else_type, f"types of if-branches have to match.\n\t\tthen-branch has type {then_type}\n\t\telse-branch has type {else_type}")
            s_new(env)
            s = s_new(s)

            return s, s(then_type)

        case LambdaExpression(arg_names, body, rest_arg):
            env = env.push()

            arg_types = [TypeVar.new() for _ in range(len(arg_names))]
            if rest_arg:
                rest_type = arg_types[-1]
                arg_types[-1] = TypeFunc('array', [rest_type])

            for arg_name, arg_type in zip(arg_names, arg_types):
                env[arg_name].type = arg_type

            s, t1 = algorithm_w(env, body)

            if rest_arg:
                arg_types[-1] = rest_type

            return s, s(FunctionType(t1, arg_types, rest_arg))

        case CallExpression(f, arg_exprs):
            s, func_type = algorithm_w(env, f)
            s(env)

            arg_types = []
            for arg_expr in arg_exprs:
                s_new, arg_type = algorithm_w(env, arg_expr)
                s_new(env)
                s = s_new(s)
                arg_types.append(arg_type)

            ret_type = TypeVar.new()
            s_new = unify(s(func_type), s(FunctionType(ret_type, arg_types)), f"called value has to have type {generalise(func_type, env)}\n\t\targuments have types {', '.join(map(str, arg_types))}")
            s = s_new(s)
            return s, s(ret_type)
