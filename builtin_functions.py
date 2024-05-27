from typing import Callable

from environment import Value, Environment
from syntaxtree.functions import BuiltInFunction
from type_checker.types import Type, TypeFunc


def register(env: Environment, name: str, t: Type, function: Callable):
    env[name] = Value(BuiltInFunction(function), t)


def register_builtin_functions(env):
    i = TypeFunc('Int', [])
    b = TypeFunc('Bool', [])
    iii = TypeFunc('->', [i, i, i])
    iib = TypeFunc('->', [i, i, b])
    bbb = TypeFunc('->', [b, b, b])

    register(env, '+', iii,    lambda v1, v2: v1 + v2)
    register(env, '-', iii,    lambda v1, v2: v1 - v2)
    register(env, '*', iii,    lambda v1, v2: v1 * v2)
    register(env, '/', iii,    lambda v1, v2: v1 / v2)
    register(env, '<', iib,    lambda v1, v2: v1 < v2)
    register(env, '>', iib,    lambda v1, v2: v1 > v2)
    register(env, '<=', iib,   lambda v1, v2: v1 <= v2)
    register(env, '>=', iib,   lambda v1, v2: v1 >= v2)
    register(env, '=', iib,    lambda v1, v2: v1 == v2)
    register(env, '!=', iib,   lambda v1, v2: v1 != v2)
    register(env, 'EQ', bbb,   lambda v1, v2: v1 == v2)
    register(env, 'NEQ', bbb,  lambda v1, v2: v1 != v2)
    register(env, 'XOR', bbb,  lambda v1, v2: v1 != v2)
    register(env, 'AND', bbb,  lambda v1, v2: v1 and v2)
    register(env, 'OR', bbb,   lambda v1, v2: v1 or v2)
    register(env, 'NAND', bbb, lambda v1, v2: not (v1 and v2))
    register(env, 'NOR', bbb,  lambda v1, v2: not (v1 or v2))
    register(env, 'IMP', bbb,  lambda v1, v2: not v1 or v2)
    register(env, 'NOT', bbb,  lambda v1: not v1)
