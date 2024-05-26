from syntaxtree.syntaxtree import *
from environment import *
from dataclasses import dataclass


@dataclass
class Closure:
    env: Environment
    arg: str
    body: Expression


@dataclass
class LambdaExpression(Expression):
    arg_name: str
    body: Expression


@dataclass
class CallExpression(Expression):
    lmbd: Expression
    arg: Expression
