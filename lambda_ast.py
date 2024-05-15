from syntaxtree import *
from environment import *

class LambdaExpression(Expression):
    def __init__(self, var, body):
        self.var = var
        self.body = body
    
    def eval(self, env):
        env = env.push()

        def closure(arg):
            env.define_local(self.var, Value(arg))
            return self.body.eval(env)
        
        return closure
    
class CallExpression(Expression):
    def __init__(self, name, arg):
        self.name = name
        self.arg = arg

    def eval(self, env):
        closure = env[self.name].value
        return closure(self.arg.eval(env))