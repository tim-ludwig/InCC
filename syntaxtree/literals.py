from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class NumberLiteral(Expression):
    value: str


@dataclass
class BoolLiteral(Expression):
    value: str


@dataclass
class StringLiteral(Expression):
    value: str


@dataclass
class CharLiteral(Expression):
    value: str


@dataclass
class ArrayLiteral(Expression):
    elements: list[Expression]
