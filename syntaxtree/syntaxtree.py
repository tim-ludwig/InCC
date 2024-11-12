from dataclasses import dataclass
from typing import Tuple

@dataclass
class Expression:
    line_span: Tuple[int, int]
    pass


class TrapExpression(Expression):
    pass