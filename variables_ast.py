from environment import Value
from syntaxtree import *

class VariableWrite(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def eval(self, env):
        result, env = self.expr.eval(env)
        env[self.name] = Value(result)
        return result, env

class VariableRead(Expression):
    def __init__(self, name):
        self.name = name
    
    def eval(self, env):
        return env[self.name].value, env

class VariableLock(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env)

class LetRecExpression(Expression):
    def __init__(self, assignment, body):
        self.assignment = assignment
        self.body = body

    def eval(self, env):
        env = env.push()
        
        name = self.assignment.name
        expr = self.assignment.expr
        
        env.define_local(name, Value(None))
        result, env = expr.eval(env)
        env[name] = Value(result)
        
        result, env = self.body.eval(env)
        return result, env.pop()