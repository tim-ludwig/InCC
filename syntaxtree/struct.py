from dataclasses import dataclass

from syntaxtree.syntaxtree import Expression
from syntaxtree.variables import AssignExpression


@dataclass
class StructExpression(Expression):
    initializers: list[AssignExpression]
    parent_expr: Expression = None


@dataclass
class MemberAccessExpression(Expression):
    expr: Expression
    member: str
    up_count: int
