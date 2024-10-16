from dataclasses import dataclass
from typing import Tuple

from syntaxtree.syntaxtree import Expression


@dataclass
class UnaryOperatorExpression(Expression):
    operator: str
    operand: Expression


@dataclass
class BinaryOperatorExpression(Expression):
    operator: str
    operands: Tuple[Expression, Expression]
