from dataclasses import dataclass
from syntaxtree.syntaxtree import Expression


@dataclass
class ImportExpression(Expression):
    path: str
