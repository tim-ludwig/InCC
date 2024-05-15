from syntaxtree import *

class NumberLiteral(Expression):
    def __init__(self, e):
        self.e = e

    def eval(self, env):
        return float(self.e), env

class BoolLiteral(Expression):
    def __init__(self, e):
        self.e = e

    def eval(self, env):
        return self.e.lower() == 'true', env