from dataclasses import dataclass


class Type:
    pass


@dataclass
class TypeVar(Type):
    name: str


@dataclass
class TypeFunc(Type):
    name: str
    args: list[Type]


@dataclass
class PolyType(Type):
    bound_var: TypeVar
    t: Type
