from syntaxtree.syntaxtree import Expression
from dataclasses import dataclass


@dataclass
class LoopExpression(Expression):
    count: Expression
    body: Expression


@dataclass
class WhileExpression(Expression):
    condition: Expression
    body: Expression


@dataclass
class DoWhileExpression(Expression):
    condition: Expression
    body: Expression


@dataclass
class IfExpression(Expression):
    condition: Expression
    then_body: Expression
    else_body: Expression


@dataclass
class RepeatExpression(Expression):
    body: Expression
