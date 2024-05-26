from syntaxtree.syntaxtree import *
from environment import *
from dataclasses import dataclass


@dataclass
class Closure:
    env: Environment
    arg_names: list[str]
    body: Expression


@dataclass
class LambdaExpression(Expression):
    arg_names: list[str]
    body: Expression


@dataclass
class CallExpression(Expression):
    lmbd: Expression
    args: list[Expression]
