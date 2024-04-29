from syntaxtree import *

class LoopExpression(Expression):
    def __init__(self, count_expr, body):
        self.count_expr = count_expr
        self.body = body
    
    def typecheck(self, vars):
        vars = self.count_expr.typecheck(vars)
        
        if self.count_expr.type != 'number':
            raise TypeError(f"count expression of loop has to have type 'number' but has type '{self.count_expr.type}'")
        
        vars = self.body.typecheck(vars)
        self.type = self.body.type

        return vars
    
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
    
    def typecheck(self, vars):
        vars = self.inital_assign.typecheck(vars)
        vars = self.condition.typecheck(vars)

        if self.condition.type != 'bool':
            raise TypeError(f"condition of for has to have type 'bool' but has type '{self.condition.type}'")
        
        vars = self.reassign.typecheck(vars)
        vars = self.body.typecheck(vars)
        self.type = self.body.type

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
    
    def typecheck(self, vars):
        vars = self.condition.typecheck(vars)

        if self.condition.type != 'bool':
            raise TypeError(f"condition of while has to have type 'bool' but has type '{self.condition.type}'")
        
        vars = self.body.typecheck(vars)
        self.type = self.body.type

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

    def typecheck(self, vars):
        vars = self.body.typecheck(vars)
        vars = self.condition.typecheck(vars)

        if self.condition.type != 'bool':
            raise TypeError(f"condition of do-while has to have type 'bool' but has type '{self.condition.type}'")
        
        self.type = self.body.type

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

    def typecheck(self, vars):
        vars = self.condition.typecheck(vars)

        if self.condition.type != 'bool':
            raise TypeError(f"condition of if has to have type 'bool' but has type '{self.condition.type}'")
        
        vars = self.then_body.typecheck(vars)
        if self.else_body:
            vars = self.else_body.typecheck(vars)

            if self.then_body.type != self.else_body.type:
                raise TypeError(f"if-the-else body type mismatch. if branch has type '{self.then_body.type}' else branch has type {self.else_body.type}")

        self.type = self.then_body.type

    def eval(self, env):
        con, env = self.condition.eval(env)
        if con:
            return self.then_body.eval(env)
        elif self.else_body:
            return self.else_body.eval(env)
        else:
            return None, env