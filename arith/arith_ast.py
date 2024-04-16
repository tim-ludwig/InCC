class Expression:
    def __init__(self):
        pass

class NumberExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def eval(self):
        return float(self.e)

class BoolLiteralExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def eval(self):
        return bool(self.e)

class ParenExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def eval(self):
        return self.e.eval()

class PlusExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() + self.e2.eval()
    
class MinusExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() - self.e2.eval()
    
class TimesExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() * self.e2.eval()
    
class DivideExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() / self.e2.eval()
    
class LessExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() < self.e2.eval()
    
class GreaterExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() > self.e2.eval()
    
class LessEqualExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() <= self.e2.eval()
    
class GreaterEqualExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() >= self.e2.eval()
    
class EqualExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() == self.e2.eval()
    
class NotEqualExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() != self.e2.eval()
    
class NotExpression(Expression):
    def __init__(self, e):
        self.e = e
    
    def eval(self):
        return not self.e().eval()
    
class AndExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() and self.e2.eval()
    
class OrExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        return self.e1.eval() or self.e2.eval()
    
class NandExpression(Expression):
    def __init__(self, e1, e2):
        self = NotExpression(AndExpression(e1, e2))
    
class NorExpression(Expression):
    def __init__(self, e1, e2):
        self = NotExpression(OrExpression(e1, e2))
    
class ImpExpression(Expression):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    
    def eval(self):
        v1 = self.e1.eval()
        v2 = self.e2.eval()
        return v2 if v1 else 1
    
binop_expressions = {
    '+' : PlusExpression,
    '-' : MinusExpression,
    '*' : TimesExpression,
    '/' : DivideExpression,
    '<' : LessExpression,
    '>' : GreaterExpression,
    '<=' : LessEqualExpression,
    '>=' : GreaterEqualExpression,
    '=' : EqualExpression,
    'eq' : EqualExpression,
    '!=' : NotEqualExpression,
    'neq' : NotEqualExpression,
    'xor' : NotEqualExpression,
    'and' : AndExpression,
    'or' : OrExpression,
    'nand' : NandExpression,
    'nor' : NorExpression,
    'imp' : ImpExpression
}