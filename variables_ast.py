from syntaxtree import *

class VariableWrite(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def typecheck(self, vars):
        vars = self.expr.typecheck(vars)
        self.type = self.expr.type
        vars[self.name] = self.type
        return vars
    
    def eval(self, env):
        result, env = self.expr.eval(env)
        env[self.name] = result
        return result, env

class VariableRead(Expression):
    def __init__(self, name):
        self.name = name

    def typecheck(self, vars):
        self.type = vars[self.name]
        return vars
    
    def eval(self, env):
        return env[self.name], env
