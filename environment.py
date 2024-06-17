from typing import Any


class Value:
    def __init__(self, value: Any=None, writeable=True):
        self.value = value
        self.writeable = writeable

    def __str__(self):
        return f'Value({str(self.value)})'

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
        env = self
        while env is not None and name not in env.vars:
            env = env.parent

        if env is None:
            env = self
            env.vars[name] = Value()

        return env.vars[name]

    def create_local(self, *names: list[str]):
        for name in names:
            self.vars[name] = Value()

    def push(self):
        return Environment(self)

    def pop(self):
        return self.parent

    def __str__(self):
        if self.parent:
            return str(self.parent) + str(self.vars)
        else:
            return str(self.vars)
