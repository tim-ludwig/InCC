from syntaxtree import *

class Sequence(Expression):
    def __init__(self, exprs):
        self.exprs = exprs

    def eval(self, env):
        result = None
        for expr in self.exprs:
            result = expr.eval(env)
        
        return result