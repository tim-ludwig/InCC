from dataclasses import dataclass

from syntaxtree.syntaxtree import Expression


@dataclass
class OperatorExpression(Expression):
    operator: str
    operands: list[Expression]
