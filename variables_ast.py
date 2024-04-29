from syntaxtree import *

class VariableWrite(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def typecheck(self, vars):
        vars = self.expr.typecheck(vars)
        if self.name in vars:
            if self.expr.type != vars[self.name]:
                raise TypeError(f"Variable '{self.name}' already has type '{vars[self.name]}' but is assigned a value of type '{self.expr.type}'")
        
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
