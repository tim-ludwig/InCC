from environment import Environment, Value
from syntaxtree.controlflow import IfExpression, LoopExpression, WhileExpression, DoWhileExpression
from syntaxtree.functions import LambdaExpression, CallExpression
from syntaxtree.literals import BoolLiteral, NumberLiteral
from syntaxtree.sequences import SequenceExpression
from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import VariableExpression, AssignExpression, LocalExpression, LockExpression
from type_inference.substitution import Substitution
from type_inference.types import Type, MonoType, TypeScheme, TypeVar, TypeFunc, FunctionType


def instantiate(ty: Type) -> MonoType:
    match ty:
        case MonoType():
            return ty

        case TypeScheme(bound_var, t):
            s = Substitution({bound_var: TypeVar.new()})
            return s(instantiate(t))


def generalise(ty: Type, env: Environment) -> Type:
    for name, v in enumerate(ty.free_vars() - env.free_type_vars(), start=ord('a')):
        ty = TypeScheme("'" + chr(name), Substitution({v: TypeVar("'" + chr(name))})(ty))

    return ty


def unify(t1: MonoType, t2: MonoType) -> Substitution:
    match t1:
        case TypeVar(name1):
            match t2:
                case TypeVar(name2):
                    if name1 == name2:
                        return Substitution({})
                    else:
                        return Substitution({name2: t1})

                case TypeFunc():
                    if name1 in t2.free_vars():
                        raise TypeError('Infinite type on unify')
                    return Substitution({name1: t2})

        case TypeFunc(name1, args1):
            match t2:
                case TypeVar():
                    return unify(t2, t1)

                case TypeFunc(name2, args2):
                    if name1 != name2 or len(args1) != len(args2):
                        raise TypeError(f"Types '{t1}' and '{t2}' don't match.")
                    else:
                        s = Substitution({})

                        for arg1, arg2 in zip(args1, args2):
                            s = s(unify(s(arg1), s(arg2)))

                        return s


def infer_type(env: Environment, exp: Expression) -> Type:
    t = TypeVar.new()
    s = algorithm_m(env, exp, t)
    return s(t)


def algorithm_m(env: Environment, expr: Expression, ty: MonoType) -> Substitution:
    match expr:
        case NumberLiteral(value): return unify(ty, TypeFunc('Float', []))
        case BoolLiteral(value): return unify(ty, TypeFunc('Bool', []))

        case AssignExpression(name, expression):
            s = algorithm_m(env, expression, ty)

            if name not in env:
                env[name] = Value(None, generalise(s(ty), s(env)))
            else:
                if not env[name].writeable:
                    raise TypeError(f"Variable '{name}' is not modifiable")
                s = unify(s(ty), s(env[name].type))
                env[name].type = generalise(s(ty), s(env))

            s(env)
            return s

        case VariableExpression(name):
            if name not in env:
                raise TypeError(f"Unknown variable '{name}'.")
            return unify(ty, instantiate(env[name].type))

        case LockExpression(name, body):
            if name not in env:
                raise TypeError(f"Unknown variable '{name}'.")
            pre_lock = env[name].writeable
            env[name].writeable = False

            s = algorithm_m(env, body, ty)
            s(env)

            env[name].writeable = pre_lock
            return s

        case LocalExpression(assignment, body):
            t = TypeVar.new()
            env = env.push()
            env.define_local(assignment.name, Value(None, t))
            s1 = algorithm_m(env, assignment.expression, t)
            s1(env)
            env[assignment.name].type = generalise(s1(t), env)
            s2 = algorithm_m(env, body, s1(ty))
            return s2(s1)

        case SequenceExpression(expressions):
            s = Substitution({})
            expr_types = [TypeVar.new() for _ in range(len(expressions))]

            for expr, expr_type in zip(expressions, expr_types):
                s_new = algorithm_m(env, expr, s(expr_type))
                s_new(env)
                s = s_new(s)

            return unify(ty, s(expr_types[-1]))(s)

        case LoopExpression(count, body):
            s1 = algorithm_m(env, count, TypeFunc('Float', []))
            s2 = algorithm_m(s1(env), body, ty)
            s2(env)
            return s2(s1)

        case WhileExpression(condition, body):
            s1 = algorithm_m(env, condition, TypeFunc('Bool', []))
            s2 = algorithm_m(s1(env), body, ty)
            s2(env)
            return s2(s1)

        case DoWhileExpression(condition, body):
            s1 = algorithm_m(env, body, ty)
            s2 = algorithm_m(s1(env), condition, TypeFunc('Bool', []))
            s2(env)
            return s2(s1)

        case IfExpression(condition, then_body, else_body):
            s = algorithm_m(env, condition, TypeFunc('Bool', []))
            s(env)

            s_new = algorithm_m(env, then_body, s(ty))
            s_new(env)
            s = s_new(s)

            s_new = algorithm_m(env, else_body, s(ty))
            s_new(env)
            s = s_new(s)
            return s

        case LambdaExpression(arg_names, body):
            arg_types = [TypeVar.new() for _ in range(len(arg_names))]
            ret_type = TypeVar.new()
            s1 = unify(ty, FunctionType(arg_types, ret_type))

            env = env.push()
            env.vars = {arg_name: Value(None, arg_type) for arg_name, arg_type in zip(arg_names, arg_types)}
            s1(env)
            s2 = algorithm_m(env, body, s1(ret_type))
            s2(env)
            return s2(s1)

        case CallExpression(f, arg_exprs):
            arg_types = [TypeVar.new() for _ in range(len(arg_exprs))]

            s = algorithm_m(env, f, FunctionType(arg_types, ty))
            s(env)
            for arg_expr, arg_type in zip(arg_exprs, arg_types):
                s_new = algorithm_m(env, arg_expr, s(arg_type))
                s_new(env)
                s = s_new(s)

            return s
