from syntaxtree import *

class VariableWrite(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def typecheck(self, vars):
        vars = self.expr.typecheck(vars)
        if self.name in vars:
            if self.expr.type != vars[self.name]['type']:
                raise TypeError(f"Variable '{self.name}' already has type '{vars[self.name]['type']}' but is assigned a value of type '{self.expr.type}'")
        
            if not vars[ſelf.name]['writeable']:
                raise AssertionError(f"Variable '{self.name}' is not writeable")
        
        self.type = self.expr.type
        vars[self.name] = {'type': self.type, 'writeable': True}
        return vars
    
    def eval(self, env):
        result, env = self.expr.eval(env)
        env[self.name] = result
        return result, env

class VariableRead(Expression):
    def __init__(self, name):
        self.name = name

    def typecheck(self, vars):
        if self.name not in vars:
                raise KeyError(f"Undefined variable '{self.name}'")
        
        self.type = vars[self.name]['type']
        return vars
    
    def eval(self, env):
        return env[self.name], env

class VariableLock(Expression):
    def __init__(self, vars, expr):
        self.vars = vars
        self.expr = expr
    
    def typecheck(self, vars):
        pre_lock = {}
        for var in self.vars:
            if var not in vars:
                raise KeyError(f"Undefined variable '{var}'")
            
            pre_lock[var] = vars[var]['writeable']
            vars[var]['writeable'] = False
        
        vars = self.expr.typecheck(vars)

        for var in self.vars:
            vars[var]['writeable'] = pre_lock[var]

        self.type = self.expr.type
        return vars

    def eval(self, env):
        return self.expr.eval(env)