from environment import Value
from syntaxtree import *

class VariableWrite(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def typecheck(self, vars):
        vars = self.expr.typecheck(vars)
        if self.name in vars:
            if self.expr.type != vars[self.name].type:
                raise TypeError(f"Variable '{self.name}' already has type '{vars[self.name].type}' but is assigned a value of type '{self.expr.type}'")
        
            if not vars[self.name].writeable:
                raise AssertionError(f"Variable '{self.name}' is not writeable")
        
        self.type = self.expr.type
        vars[self.name] = Value(None, self.type)
        return vars
    
    def eval(self, env):
        result, env = self.expr.eval(env)
        env[self.name] = Value(result, self.expr.type)
        return result, env

class VariableRead(Expression):
    def __init__(self, name):
        self.name = name

    def typecheck(self, vars):
        if self.name not in vars:
                raise KeyError(f"Undefined variable '{self.name}'")
        
        self.type = vars[self.name].type
        return vars
    
    def eval(self, env):
        return env[self.name].value, env

class VariableLock(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def typecheck(self, vars):
        if self.name not in vars:
            raise KeyError(f"Undefined variable '{self.name}'")
        
        pre_lock = vars[self.name].writeable
        vars[self.name].writeable = False
        
        vars = self.expr.typecheck(vars)

        vars[self.name].writeable = pre_lock

        self.type = self.expr.type
        return vars

    def eval(self, env):
        return self.expr.eval(env)

class LetRecExpression(Expression):
    def __init__(self, assignment, body):
        self.assignment = assignment
        self.body = body

    def typecheck(self, vars):
        vars = vars.push()

        name = self.assignment.name
        expr = self.assignment.expr

        vars.define_local(name, Value(None, expr.type))
        vars = expr.typecheck(vars)
        
        vars = self.body.typecheck(vars)
        self.type = self.body.type

        return vars.pop()

    def eval(self, env):
        env = env.push()
        
        name = self.assignment.name
        expr = self.assignment.expr
        
        env.define_local(name, Value(None, expr.type))
        result, env = expr.eval(env)
        env[name] = Value(result, expr.type)
        
        result, env = self.body.eval(env)
        return result, env.pop()