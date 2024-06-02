from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class LambdaExpression(Expression):
    arg_names: list[str]
    body: Expression
    rest_arg: bool = False


@dataclass
class FunctionExpression(Expression):
    func_name: str
    arg_names: list[str]
    body: Expression


@dataclass
class CallExpression(Expression):
    f: Expression
    arg_exprs: list[Expression]
