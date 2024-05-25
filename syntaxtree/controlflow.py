from syntaxtree.syntaxtree import *


class LoopExpression(Expression):
    def __init__(self, count_expr, body):
        self.count_expr = count_expr
        self.body = body
    
    def eval(self, env):
        count = self.count_expr.eval(env)
        
        result = None
        for _ in range(int(count)):
            result = self.body.eval(env)

        return result


class ForExpression(Expression):
    def __init__(self, initial_assign, condition, reassign, body):
        self.inital_assign = initial_assign
        self.condition = condition
        self.reassign = reassign
        self.body = body

    def eval(self, env):
        _ = self.inital_assign.eval(env)

        result = None
        while True:
            con = self.condition.eval(env)
            if not con:
                break

            result = self.body.eval(env)
            _ = self.reassign.eval(env)

        return result


class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        result = None
        while True:
            con = self.condition.eval(env)
            if not con:
                break

            result = self.body.eval(env)

        return result


class DoWhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        result = None
        while True:
            result = self.body.eval(env)

            con = self.condition.eval(env)
            if not con:
                break

        return result


class IfExpression(Expression):
    def __init__(self, condition, then_body, else_body):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def eval(self, env):
        con = self.condition.eval(env)
        if con:
            return self.then_body.eval(env)
        elif self.else_body:
            return self.else_body.eval(env)
        else:
            return None
