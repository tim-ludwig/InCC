class Expression: pass

class NumberExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.type = 'number'

    def eval(self):
        return float(self.e)
    
    def s_expression(self):
        return str(self.e)

class BoolLiteralExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.type = 'bool'

    def eval(self):
        return self.e.lower() == 'true'
    
    def s_expression(self):
        return 't' if self.eval() else 'nil'

class ParenExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.e.typecheck()
        self.type = self.e.type

    def eval(self):
        return self.e.eval()
    
    def s_expression(self):
        return self.e.s_expression()

class NotExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.e.typecheck()

        if self.e.type != 'bool':
            raise TypeError(f'operand types not applicable: not {self.e.type}')

        self.type = 'bool'

    def eval(self):
        return not self.e.eval()
    
    def s_expression(self):
        return f'(not {self.e.s_expression()})'

class BinaryOperator(Expression):
    operators = dict()

    @classmethod
    def register(cls, operator, argument_types, return_type, action):
        if operator not in cls.operators:
            cls.operators[operator] = dict()
        
        cls.operators[operator][argument_types] = (return_type, action)

    def __init__(self, op, e1, e2):
        self.op = op
        self.e1 = e1
        self.e2 = e2
    
    def typecheck(self):
        self.e1.typecheck()
        self.e2.typecheck()
        t1 = self.e1.type
        t2 = self.e2.type

        instances = BinaryOperator.operators[self.op]
        
        if (t1, t2) not in instances:
            alternatives = '\n'.join([f"\t{t1} {self.op} {t2} : {tr}" for ((t1, t2), (tr, _)) in instances.items()])
            raise TypeError(
                f"No instance of operator '{self.op}' has argument types '{t1}' and '{t2}'.\n"
                "Possible signatures are:\n"
                f"{alternatives}"
            )
        
        self.type, _ = instances[(t1, t2)]

    def eval(self):
        instances = BinaryOperator.operators[self.op]
        _, action = instances[(self.e1.type, self.e2.type)]
        return action(self.e1.eval(), self.e2.eval())
    
    def s_expression(self):
        return f'({self.op.lower()} {self.e1.s_expression()} {self.e2.s_expression()})'

BinaryOperator.register('+',    ('number', 'number'), 'number', lambda v1, v2: v1 + v2)
BinaryOperator.register('-',    ('number', 'number'), 'number', lambda v1, v2: v1 - v2)
BinaryOperator.register('*',    ('number', 'number'), 'number', lambda v1, v2: v1 * v2)
BinaryOperator.register('/',    ('number', 'number'), 'number', lambda v1, v2: v1 / v2)
BinaryOperator.register('<',    ('number', 'number'), 'bool',   lambda v1, v2: v1 < v2)
BinaryOperator.register('>',    ('number', 'number'), 'bool',   lambda v1, v2: v1 > v2)
BinaryOperator.register('<=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 <= v2)
BinaryOperator.register('>=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 >= v2)
BinaryOperator.register('=',    ('number', 'number'), 'bool',   lambda v1, v2: v1 == v2)
BinaryOperator.register('!=',   ('number', 'number'), 'bool',   lambda v1, v2: v1 != v2)
BinaryOperator.register('EQ',   ('bool',   'bool'),   'bool',   lambda v1, v2: v1 == v2)
BinaryOperator.register('NEQ',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 != v2)
BinaryOperator.register('XOR',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 != v2)
BinaryOperator.register('AND',  ('bool',   'bool'),   'bool',   lambda v1, v2: v1 and v2)
BinaryOperator.register('OR',   ('bool',   'bool'),   'bool',   lambda v1, v2: v1 or v2)
BinaryOperator.register('NAND', ('bool',   'bool'),   'bool',   lambda v1, v2: not (v1 and v2))
BinaryOperator.register('NOR',  ('bool',   'bool'),   'bool',   lambda v1, v2: not (v1 or v2))
BinaryOperator.register('IMP',  ('bool',   'bool'),   'bool',   lambda v1, v2: not v1 or v2)