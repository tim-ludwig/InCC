from dataclasses import dataclass


class Type:
    def free_vars(self):
        pass


class MonoType(Type):
    pass


@dataclass
class TypeVar(MonoType):
    type_var_count = 0
    name: str

    @classmethod
    def new(cls):
        n = cls.type_var_count
        cls.type_var_count += 1
        return TypeVar(f't{n}')

    def free_vars(self):
        return {self.name}

    def __str__(self):
        return self.name


@dataclass
class TypeFunc(MonoType):
    name: str
    args: list[MonoType]

    def free_vars(self):
        v = set()
        for arg in self.args:
            v |= arg.free_vars()

        return v

    def __str__(self):
        a = '' if len(self.args) == 0 else '[' + ', '.join(map(str, self.args)) + ']'
        return self.name + a


class FunctionType(TypeFunc):
    def __init__(self, args: list[MonoType], ret: MonoType):
        super().__init__('->', [*args, ret])

    def __str__(self):
        return f"({', '.join(map(str, super().args[:-1]))}) -> {str(super().args[-1])}"

@dataclass
class TypeScheme(Type):
    bound_var: str
    t: Type

    def free_vars(self):
        return self.t.free_vars() - {self.bound_var}

    def __str__(self):
        return f'V{self.bound_var}: {self.t}'
