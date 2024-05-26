from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class AssignExpression(Expression):
    name: str
    expression: Expression


@dataclass
class VariableExpression(Expression):
    name: str


@dataclass
class LockExpression(Expression):
    name: str
    body: Expression


@dataclass
class LocalExpression(Expression):
    assignment: AssignExpression
    body: Expression
