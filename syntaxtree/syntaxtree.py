from dataclasses import dataclass
from typing import Tuple

@dataclass
class Expression:
    position: Tuple[int, int] | Tuple[str, int, int]
    pass


class TrapExpression(Expression):
    pass