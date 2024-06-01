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
        if self.name == '->':
            if len(self.args) == 1:
                return f"-> {self.args[-1]}"

            arg_strs = [f"({arg_type})" if isinstance(arg_type, TypeFunc) and arg_type.name == '->' else str(arg_type) for arg_type in self.args[:-1]]
            return f"{', '.join(arg_strs)} -> {self.args[-1]}"

        a = '' if len(self.args) == 0 else '[' + ', '.join(map(str, self.args)) + ']'
        return self.name + a


@dataclass
class TypeScheme(Type):
    bound_vars: list[str]
    t: Type

    def free_vars(self):
        return self.t.free_vars() - set(self.bound_vars)

    def __str__(self):
        return str(self.t)
