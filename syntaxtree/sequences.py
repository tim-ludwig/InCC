from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class SequenceExpression(Expression):
    expressions: list[Expression]
