from syntaxtree.syntaxtree import *
from environment import Value


class AssignExpression(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def eval(self, env):
        result = self.expr.eval(env)
        env[self.name] = Value(result)
        return result


class VariableExpression(Expression):
    def __init__(self, name):
        self.name = name
    
    def eval(self, env):
        return env[self.name].value


class LockExpression(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env)


class LocalExpression(Expression):
    def __init__(self, assignment, body):
        self.assignment = assignment
        self.body = body

    def eval(self, env):
        env = env.push()
        
        name = self.assignment.name
        expr = self.assignment.expr
        
        env.define_local(name, Value(None))
        result = expr.eval(env)
        env[name] = Value(result)
        
        result = self.body.eval(env)
        return result
