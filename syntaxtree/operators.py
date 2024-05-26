from syntaxtree.syntaxtree import *
from dataclasses import dataclass


@dataclass
class OperatorExpression(Expression):
    operators = dict()
    op: str
    operands: list[Expression]

    @classmethod
    def register(cls, operator, argc, action):
        if operator not in cls.operators:
            cls.operators[operator] = dict()
        
        cls.operators[operator][argc] = action


OperatorExpression.register('+', 2, lambda v1, v2: v1 + v2)
OperatorExpression.register('-', 2, lambda v1, v2: v1 - v2)
OperatorExpression.register('*', 2, lambda v1, v2: v1 * v2)
OperatorExpression.register('/', 2, lambda v1, v2: v1 / v2)
OperatorExpression.register('<', 2, lambda v1, v2: v1 < v2)
OperatorExpression.register('>', 2, lambda v1, v2: v1 > v2)
OperatorExpression.register('<=', 2, lambda v1, v2: v1 <= v2)
OperatorExpression.register('>=', 2, lambda v1, v2: v1 >= v2)
OperatorExpression.register('=', 2, lambda v1, v2: v1 == v2)
OperatorExpression.register('!=', 2, lambda v1, v2: v1 != v2)
OperatorExpression.register('+', 1, lambda v1    : v1)
OperatorExpression.register('-', 1, lambda v1    : -v1)
OperatorExpression.register('EQ', 2, lambda v1, v2: v1 == v2)
OperatorExpression.register('NEQ', 2, lambda v1, v2: v1 != v2)
OperatorExpression.register('XOR', 2, lambda v1, v2: v1 != v2)
OperatorExpression.register('AND', 2, lambda v1, v2: v1 and v2)
OperatorExpression.register('OR', 2, lambda v1, v2: v1 or v2)
OperatorExpression.register('NAND', 2, lambda v1, v2: not (v1 and v2))
OperatorExpression.register('NOR', 2, lambda v1, v2: not (v1 or v2))
OperatorExpression.register('IMP', 2, lambda v1, v2: not v1 or v2)
OperatorExpression.register('NOT', 1, lambda v1    : not v1)
