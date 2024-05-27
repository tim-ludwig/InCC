from syntaxtree.syntaxtree import *
from environment import *
from dataclasses import dataclass
from typing import Callable


@dataclass
class Closure:
    env: Environment
    arg_names: list[str]
    body: Expression


@dataclass
class BuiltInFunction:
    func: Callable


@dataclass
class LambdaExpression(Expression):
    arg_names: list[str]
    body: Expression


@dataclass
class FunctionExpression(Expression):
    func_name: str
    arg_names: list[str]
    body: Expression


@dataclass
class CallExpression(Expression):
    f: Expression
    arg_exprs: list[Expression]
