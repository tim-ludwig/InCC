from syntaxtree import *

class LoopExpression(Expression):
    def __init__(self, count_expr, body):
        self.count_expr = count_expr
        self.body = body
    
    def eval(self, env):
        count, env = self.count_expr.eval(env)
        
        result = None
        for _ in range(int(count)):
            result, env = self.body.eval(env)

        return result, env

class ForExpression(Expression):
    def __init__(self, initial_assign, condition, reassign, body):
        self.inital_assign = initial_assign
        self.condition = condition
        self.reassign = reassign
        self.body = body

    def eval(self, env):
        _, env = self.inital_assign.eval(env)

        result = None
        while True:
            con, env = self.condition.eval(env)
            if not con:
                break

            result, env = self.body.eval(env)
            _, env = self.reassign.eval(env)

        return result, env

class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        result = None
        while True:
            con, env = self.condition.eval(env)
            if not con:
                break

            result, env = self.body.eval(env)

        return result, env

class DoWhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        result = None
        while True:
            result, env = self.body.eval(env)

            con, env = self.condition.eval(env)
            if not con:
                break

        return result, env

class IfExpression(Expression):
    def __init__(self, condition, then_body, else_body):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def eval(self, env):
        con, env = self.condition.eval(env)
        if con:
            return self.then_body.eval(env)
        elif self.else_body:
            return self.else_body.eval(env)
        else:
            return None, env