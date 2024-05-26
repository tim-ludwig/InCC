from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class NumberLiteral(Expression):
    value: str


@dataclass
class BoolLiteral(Expression):
    value: str
