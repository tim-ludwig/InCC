from dataclasses import dataclass
from typing import Any, Self


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.containing_struct = parent.containing_struct if parent else None
        self.vars = {}

    def __contains__(self, name):
        if name in self.vars:
            return True
        elif self.parent:
            return name in self.parent
        else:
            return False

    def __getitem__(self, name):
        env = self
        while env.parent is not None and name not in env.vars:
            env = env.parent

        return env.vars[name]

    def __setitem__(self, name, value):
        env = self
        while env.parent is not None and name not in env.vars:
            env = env.parent

        env.vars[name] = value


    def push(self, *names):
        env = Environment(self)

        for name in names:
            env.vars[name] = None

        return env

    def pop(self):
        return self.parent

    def root(self):
        env = self

        while env.parent is not None:
            env = env.parent

        return env

    def __str__(self):
        if self.parent:
            return str(self.parent) + str(self.vars)
        else:
            return str(self.vars)
