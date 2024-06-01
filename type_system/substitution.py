from dataclasses import dataclass

from environment import Environment, Value
from type_system.types import TypeVar, Type, TypeFunc, TypeScheme, MonoType


@dataclass
class Substitution:
    subst: dict[str, Type]

    def apply(self, t: Type):
        match t:
            case TypeVar(name):
                return self.subst[name] if name in self.subst else t

            case TypeFunc(name, args):
                return TypeFunc(name, [self.apply(arg) for arg in args])

            case TypeScheme(bound_var, s):
                return TypeScheme(bound_var, Substitution({var: rep for var, rep in self.subst.items() if var != bound_var}).apply(s))

    def apply_to_env(self, env: Environment):
        env.vars = {name: Value(v.value, self.apply(v.type)) for name, v in env.vars.items()}

        if env.parent:
            self.apply_to_env(env.parent)

        return env

    def compose(self, other):
        subst = dict()

        subst.update(self.subst)
        subst.update({var: self.apply(rep) for var, rep in other.subst.items()})

        return Substitution(subst)

    def __call__(self, val):
        match val:
            case Type():
                return self.apply(val)

            case Substitution():
                return self.compose(val)

            case Environment():
                return self.apply_to_env(val)
