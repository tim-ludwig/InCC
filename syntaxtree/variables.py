from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class AssignExpression(Expression):
    var: Expression
    expression: Expression


@dataclass
class VariableExpression(Expression):
    name: str


@dataclass
class LockExpression(Expression):
    names: list[str]
    body: Expression


@dataclass
class LocalExpression(Expression):
    assignments: list[AssignExpression]
    body: Expression
