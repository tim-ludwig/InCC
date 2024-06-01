from typing import Any
from type_inference.types import Type


class Value:
    def __init__(self, value: Any, type: Type=None, writeable=True):
        self.value = value
        self.type = type
        self.writeable = writeable

    def __str__(self):
        return f'Value({str(self.value)}, t: {self.type})' if self.type else f'Value({str(self.value)})'
    
    def __repr__(self):
        return str(self)


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def __contains__(self, name):
        if name in self.vars:
            return True
        elif self.parent:
            return name in self.parent
        else:
            return False

    def __getitem__(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent[name]
        else:
            raise KeyError(f"'{name}' not in env")

    def __setitem__(self, name, value):
        env = self
        while env.parent and name not in env.vars:
            env = env.parent

        env.vars[name] = value

    def define_local(self, name, value):
        self.vars[name] = value

    def push(self):
        return Environment(self)
    
    def pop(self):
        return self.parent

    def free_type_vars(self):
        v = set()

        for val in self.vars.values():
            v |= val.type.free_vars()

        if self.parent:
            v |= self.parent.free_type_vars()

        return v

    def __str__(self):
        if self.parent:
            return str(self.parent) + str(self.vars)
        else:
            return str(self.vars)
