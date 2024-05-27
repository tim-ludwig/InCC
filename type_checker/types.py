from dataclasses import dataclass


class Type:
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


@dataclass
class TypeFunc(MonoType):
    name: str
    args: list[MonoType]


@dataclass
class PolyType(Type):
    bound_var: TypeVar
    t: Type
