from syntaxtree import *

class NumberLiteral(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.type = 'number'

    def eval(self):
        return float(self.e)
    
    def s_expression(self):
        return str(self.e)

class BoolLiteral(Expression):
    def __init__(self, e):
        self.e = e
    
    def typecheck(self):
        self.type = 'bool'

    def eval(self):
        return self.e.lower() == 'true'
    
    def s_expression(self):
        return 't' if self.eval() else 'nil'