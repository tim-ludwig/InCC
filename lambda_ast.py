from syntaxtree import *
from environment import *


class Closure:
    def __init__(self, env, arg_name, body):
        self.env = env.push()
        self.env.define_local(arg_name, Value(None))
        self.arg_name = arg_name
        self.body = body

    def eval(self, val):
        self.env[self.arg_name] = Value(val)
        return self.body.eval(self.env)


class LambdaExpression(Expression):
    def __init__(self, arg_name, body):
        self.arg_name = arg_name
        self.body = body
    
    def eval(self, env):
        return Closure(env, self.arg_name, self.body)


class CallExpression(Expression):
    def __init__(self, lmbd, arg):
        self.lmbd = lmbd
        self.arg = arg

    def eval(self, env):
        closure = self.lmbd.eval(env)
        return closure.eval(self.arg.eval(env))
