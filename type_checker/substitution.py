from dataclasses import dataclass

from environment import Environment, Value
from type_checker.types import TypeVar, Type, TypeFunc, PolyType, MonoType


@dataclass
class Substitution:
    subst: dict[str, Type]

    def apply(self, t: Type):
        match t:
            case TypeVar(name):
                return self.subst[name] if name in self.subst else t

            case TypeFunc(name, args):
                return TypeFunc(name, [self.apply(arg) for arg in args])

            case PolyType(bound_var, s):
                return PolyType(bound_var, Substitution({var: rep for var, rep in self.subst.items() if var != bound_var.name}).apply(s))

    def apply_to_env(self, env: Environment):
        env.vars = {name: Value(v.value, self.apply(v.type)) for name, v in env.vars.items()}

        if env.parent:
            self.apply_to_env(env.parent)

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


def instantiate(ty: Type) -> MonoType:
    match ty:
        case MonoType():
            return ty

        case PolyType(bound_var, t):
            s = Substitution({bound_var.name: TypeVar.new()})
            return s(instantiate(t))


def generalise(ty: Type, env: Environment) -> Type:
    for v in ty.free_vars() - env.free_type_vars():
        ty = PolyType(TypeVar(v), ty)

    return ty


def unify(t1: MonoType, t2: MonoType) -> Substitution:
    match t1:
        case TypeVar(name1):
            match t2:
                case TypeVar(name2):
                    if name1 == name2:
                        return Substitution({})
                    else:
                        return Substitution({name2: t1})

                case TypeFunc():
                    return Substitution({name1: t2})

        case TypeFunc(name1, args1):
            match t2:
                case TypeVar(name2):
                    return Substitution({name2: t1})

                case TypeFunc(name2, args2):
                    if name1 != name2:
                        raise TypeError(f"Types '{name1}' and '{name2}' don't match.")
                    else:
                        s = Substitution({})

                        for arg1, arg2 in zip(args1, args2):
                            s = s(unify(arg1, arg2))

                        return s