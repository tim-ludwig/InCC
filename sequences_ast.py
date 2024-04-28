from syntaxtree import *

class Sequence(Expression):
    def __init__(self, exprs):
        self.exprs = exprs
    
    def typecheck(self, vars):
        for expr in self.exprs:
            vars = expr.typecheck(vars)
        
        self.type = self.exprs[-1].type
        return vars

    def eval(self, env):
        result = None
        for expr in self.exprs:
            result, env = expr.eval(env)
        
        return result, env