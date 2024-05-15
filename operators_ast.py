from syntaxtree import *

class Operator(Expression):
    operators = dict()

    @classmethod
    def register(cls, operator, argc, action):
        if operator not in cls.operators:
            cls.operators[operator] = dict()
        
        cls.operators[operator][argc] = action

    def __init__(self, op, *operands):
        self.op = op
        self.operands = operands

    def eval(self, env):
        args = []
        for operand in self.operands:
            result = operand.eval(env)
            args.append(result)
        
        result = Operator.operators[self.op][len(args)](*args)
        return result

Operator.register('+',    2, lambda v1, v2: v1 + v2)
Operator.register('-',    2, lambda v1, v2: v1 - v2)
Operator.register('*',    2, lambda v1, v2: v1 * v2)
Operator.register('/',    2, lambda v1, v2: v1 / v2)
Operator.register('<',    2, lambda v1, v2: v1 < v2)
Operator.register('>',    2, lambda v1, v2: v1 > v2)
Operator.register('<=',   2, lambda v1, v2: v1 <= v2)
Operator.register('>=',   2, lambda v1, v2: v1 >= v2)
Operator.register('=',    2, lambda v1, v2: v1 == v2)
Operator.register('!=',   2, lambda v1, v2: v1 != v2)
Operator.register('+',    1, lambda v1    : v1)
Operator.register('-',    1, lambda v1    : -v1)
Operator.register('EQ',   2, lambda v1, v2: v1 == v2)
Operator.register('NEQ',  2, lambda v1, v2: v1 != v2)
Operator.register('XOR',  2, lambda v1, v2: v1 != v2)
Operator.register('AND',  2, lambda v1, v2: v1 and v2)
Operator.register('OR',   2, lambda v1, v2: v1 or v2)
Operator.register('NAND', 2, lambda v1, v2: not (v1 and v2))
Operator.register('NOR',  2, lambda v1, v2: not (v1 or v2))
Operator.register('IMP',  2, lambda v1, v2: not v1 or v2)
Operator.register('NOT',  1, lambda v1    : not v1)