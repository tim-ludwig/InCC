from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Value:
    value: Any = None
    writeable: bool = True


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
        while env is not None and name not in env.vars:
            env = env.parent

        if env is None:
            env = self
            env.vars[name] = Value()

        return env.vars[name]

    def push(self, *names):
        env = Environment(self)

        for name in names:
            env.vars[name] = Value()

        return env

    def pop(self):
        return self.parent

    def __str__(self):
        if self.parent:
            return str(self.parent) + str(self.vars)
        else:
            return str(self.vars)
