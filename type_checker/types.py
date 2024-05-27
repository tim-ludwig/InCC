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


@dataclass
class TypeFunc(MonoType):
    name: str
    args: list[MonoType]

    def free_vars(self):
        v = set()
        for arg in self.args:
            v |= arg.free_vars()

        return v


@dataclass
class PolyType(Type):
    bound_var: TypeVar
    t: Type

    def free_vars(self):
        return self.t.free_vars() - {self.bound_var.name}
