from typing import Callable

from environment import Value, Environment
from syntaxtree.lmbd import BuiltInFunction


def register(env: Environment, name: str, function: Callable):
    env[name] = Value(BuiltInFunction(function))


def register_builtin_functions(env):
    register(env, '+',    lambda v1, v2: v1 + v2)
    register(env, '-',    lambda v1, v2: v1 - v2)
    register(env, '*',    lambda v1, v2: v1 * v2)
    register(env, '/',    lambda v1, v2: v1 / v2)
    register(env, '<',    lambda v1, v2: v1 < v2)
    register(env, '>',    lambda v1, v2: v1 > v2)
    register(env, '<=',   lambda v1, v2: v1 <= v2)
    register(env, '>=',   lambda v1, v2: v1 >= v2)
    register(env, '=',    lambda v1, v2: v1 == v2)
    register(env, '!=',   lambda v1, v2: v1 != v2)
    register(env, 'EQ',   lambda v1, v2: v1 == v2)
    register(env, 'NEQ',  lambda v1, v2: v1 != v2)
    register(env, 'XOR',  lambda v1, v2: v1 != v2)
    register(env, 'AND',  lambda v1, v2: v1 and v2)
    register(env, 'OR',   lambda v1, v2: v1 or v2)
    register(env, 'NAND', lambda v1, v2: not (v1 and v2))
    register(env, 'NOR',  lambda v1, v2: not (v1 or v2))
    register(env, 'IMP',  lambda v1, v2: not v1 or v2)
    register(env, 'NOT',  lambda v1: not v1)
