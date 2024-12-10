from dataclasses import dataclass
from typing import Tuple

@dataclass
class Expression:
    position: Tuple[int, int] | Tuple[str, int, int]
    pass


@dataclass
class Program(Expression):
    expr: Expression
    pass


@dataclass
class TrapExpression(Expression):
    pass