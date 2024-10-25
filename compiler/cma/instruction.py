from dataclasses import dataclass


@dataclass
class Instruction:
    def __str__(self):
        return self.__class__.__name__


@dataclass
class loadc(Instruction):
    value: int

    def __str__(self):
        return f'loadc {self.value}'


@dataclass
class loadrc(Instruction):
    value: int

    def __str__(self):
        return f'loadrc {self.value}'


@dataclass
class pop(Instruction): pass


@dataclass
class dup(Instruction): pass


@dataclass
class swap(Instruction): pass


@dataclass
class operator(Instruction):
    op: str

    def __str__(self):
        return self.op


@dataclass
class load(Instruction): pass


@dataclass
class store(Instruction): pass


@dataclass
class label(Instruction):
    name: str
    def __str__(self):
        return self.name + ':'


@dataclass
class jump(Instruction):
    label: str

    def __str__(self):
        return f'jump {self.label}'


@dataclass
class jumpz(Instruction):
    label: str

    def __str__(self):
        return f'jumpz {self.label}'


@dataclass
class mark(Instruction): pass


@dataclass
class call(Instruction): pass


@dataclass
class enter(Instruction): pass


@dataclass
class alloc(Instruction):
    size: int

    def __str__(self):
        return f'alloc {self.size}'


@dataclass
class ret(Instruction): pass


@dataclass
class slide(Instruction):
    discard: int
    keep: int

    def __str__(self):
        return f'slide {self.discard} {self.keep}'
