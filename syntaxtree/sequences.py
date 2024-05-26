from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class Sequence(Expression):
    expressions: list[Expression]
