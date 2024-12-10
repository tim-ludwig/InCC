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
class ProcedureExpression(Expression):
    arg_names: list[str]
    local_names: list[str]
    body: Expression


@dataclass
class CallExpression(Expression):
    f: Expression
    arg_exprs: list[Expression]


@dataclass
class ReturnExpression(Expression):
    val: Expression


@dataclass
class QuitExpression(Expression):
    val: Expression
