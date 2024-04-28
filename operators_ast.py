from syntaxtree import *

class Operator(Expression):
    operators = dict()

    @classmethod
    def register(cls, operator, operand_types, return_type, action):
        if operator not in cls.operators:
            cls.operators[operator] = dict()
        
        cls.operators[operator][operand_types] = (return_type, action)

    def __init__(self, op, *operands):
        self.op = op
        self.operands = operands
    
    def typecheck(self):
        for operand in self.operands:
            operand.typecheck()
        
        self.operand_types = tuple([operand.type for operand in self.operands])
        instances = Operator.operators[self.op]
        
        if self.operand_types not in instances:
            alternatives = '\n'.join([f"\t{self.op} : {operand_types} -> '{tr}'" for (operand_types, (tr, _)) in instances.items()])
            raise TypeError(
                f"No instance of operator '{self.op}' has operand types {self.operand_types}.\n"
                "Possible signatures are:\n"
                f"{alternatives}"
            )
        
        self.type, self.action = instances[self.operand_types]

    def eval(self):
        return self.action(*[operand.eval() for operand in self.operands])
    
    def s_expression(self):
        return f"({self.op.lower()} {' '.join([operand.s_expression() for operand in self.operands])})"

Operator.register('+',    ('number', 'number'), 'number', lambda v1, v2: v1 + v2)
Operator.register('-',    ('number', 'number'), 'number', lambda v1, v2: v1 - v2)
Operator.register('*',    ('number', 'number'), 'number', lambda v1, v2: v1 * v2)
Operator.register('/',    ('number', 'number'), 'number', lambda v1, v2: v1 / v2)
Operator.register('<',    ('number', 'number'), 'bool',   lambda v1, v2: v1 < v2)
Operator.register('>',    ('number', 'number'), 'bool',   lambda v1, v2: v1 > v2)
Operator.register('<=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 <= v2)
Operator.register('>=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 >= v2)
Operator.register('=',    ('number', 'number'), 'bool',   lambda v1, v2: v1 == v2)
Operator.register('!=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 != v2)
Operator.register('+',    ('number',),          'number', lambda v1    : v1)
Operator.register('-',    ('number',),          'number', lambda v1    : -v1)
Operator.register('EQ',   ('bool',   'bool'),   'bool',   lambda v1, v2: v1 == v2)
Operator.register('NEQ',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 != v2)
Operator.register('XOR',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 != v2)
Operator.register('AND',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 and v2)
Operator.register('OR',   ('bool',   'bool'),   'bool',   lambda v1, v2: v1 or v2)
Operator.register('NAND', ('bool',   'bool'),   'bool',   lambda v1, v2: not (v1 and v2))
Operator.register('NOR',  ('bool',   'bool'),   'bool',   lambda v1, v2: not (v1 or v2))
Operator.register('IMP',  ('bool',   'bool'),   'bool',   lambda v1, v2: not v1 or v2)
Operator.register('NOT',  ('bool',),            'bool',   lambda v1    : not v1)