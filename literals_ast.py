from syntaxtree import *

class NumberLiteral(Expression):
    def __init__(self, e):
        self.type = 'number'
        self.e = e
    
    def typecheck(self, vars):
        return vars

    def eval(self, env):
        return float(self.e), env

class BoolLiteral(Expression):
    def __init__(self, e):
        self.type = 'bool'
        self.e = e
    
    def typecheck(self, vars):
        return vars

    def eval(self, env):
        return self.e.lower() == 'true', env