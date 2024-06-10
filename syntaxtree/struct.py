from dataclasses import dataclass

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression


@dataclass
class StructExpression(Expression):
    initializers: list[AssignExpression]
