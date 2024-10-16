import builtins
import os
import re
import subprocess

from environment import Environment
from parser.parser import parse_expr
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import BinaryOperatorExpression, UnaryOperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.variables import AssignExpression, VariableExpression

unop_inst = {
    '-': ('neg',)
}
binop_inst = {
    '+': ('add',),
    '-': ('sub',),
    '*': ('mul',),
    '/': ('div',),
}


start_addr = 0
def make_global(size):
    global start_addr
    start_addr += size
    return start_addr - size


def code_r(expr, env):
    match expr:
        case NumberLiteral(value):
            return [
                ('loadc', value)
            ]
        case UnaryOperatorExpression(operator, operand):
            return [
                *code_r(operand, env),
                unop_inst[operator],
            ]
        case BinaryOperatorExpression(operator, operands):
            return [
                *code_r(operands[0], env),
                *code_r(operands[1], env),
                binop_inst[operator],
            ]

        
        case AssignExpression(name, expr):
            if name not in env:
                env[name].address = make_global(8)
                env[name].scope = 'global'
                env[name].size = 8

            return [
                *code_r(expr, env),
                ('loadc', str(env[name].address)),
                ('store',)
            ]
        case VariableExpression(name):
            return [
                ('loadc', str(env[name].address)),
                ('load',)
            ]
        case SequenceExpression(exprs):
            instructions = []
            for expr in exprs[:-1]:
                instructions += code(expr, env)
            instructions += code_r(exprs[-1], env)
            return instructions
        case _:
            raise NotImplementedError(expr)


def code(expr, env):
    return [*code_r(expr, env), ('pop',)]


def code_l(expr, env):
    match expr:
        case _:
            raise NotImplementedError(expr)


def x86_program(x86_code, env) :
    program  = x86_prefix(env)
    program += x86_start(env)
    program += "\n;;; Start des eigentlichen Programms\n"
    program += format_code(x86_code)
    program += ";;; Ende des eigentlichen Programms\n\n"
    program += x86_final(env)
    return program

def x86_prefix(env):
    program  = "extern  printf\n"
    program += "SECTION .data               ; Data section, initialized variables\n"
    program += 'i64_fmt:  db  "%lld", 10, 0 ; printf format for printing an int64\n'
    return program

def x86_start(env):
    program  = "\n"
    program += "SECTION  .text\nglobal main\n"
    main     = "main:\n"
    main    += "  push  rbp                 ; unnötig, weil es den Wert 1 enthält, trotzem notwendig, weil sonst segfault\n"
    main   += f"  sub   rsp, {env.total_size()}\n"
    main    += "  mov   rax,rsp             ; rsp zeigt auf den geretteten rbp  \n"
    main    += "  sub   rax,qword 8         ; neuer rbp sollte ein wort darüber liegen\n"
    main    += "  mov   rbp,rax             ; set frame pointer to current (empty) stack pointer\n"
    return program + format_code(main)

def x86_final(env):
    program  = "  pop   rax\n"
    program += "  mov   rsi, rax\n"
    program += "  mov   rdi,i64_fmt         ; arguments in rdi, rsi\n"
    program += "  mov   rax,0               ; no xmm registers used\n"
    program += "  push  rbp                 ; set up stack frame, must be alligned\n"
    program += "  call  printf              ; Call C function\n"
    program += "  pop   rbp                 ; restore stack\n"
    program += f"  add   rsp,{env.total_size()}\n"
    program += "\n;;; Rueckkehr zum aufrufenden Kontext\n"
    program += "  pop   rbp                 ; original rbp ist last thing on the stack\n"
    program += "  mov   rax,0               ; return 0\n"
    program += "  ret\n"
    return format_code(program)



def ir_to_asm(ir):
    if type(ir) == builtins.list:
        asm = []
        for inst in ir:
            asm += ir_to_asm(inst)
        return asm

    instructions = [f';;; {" ".join(ir)}']

    match ir:
        case ('pop',):
            instructions += [
                'pop   rax',
            ]
        case ('loadc', val):
            instructions += [
                f'push qword {val}'
            ]
        case ('neg',):
            instructions += [
                'pop   rax',
                'neg   rax',
                'push  rax',
            ]
        case ('add',):
            instructions += [
                'pop   rcx',
                'pop   rax',
                'add   rax, rcx',
                'push  rax',
            ]
        case ('sub',):
            instructions += [
                'pop   rcx',
                'pop   rax',
                'sub   rax, rcx',
                'push  rax',
            ]
        case ('mul',):
            instructions += [
                'pop   rcx',
                'pop   rax',
                'imul  rax, rcx',
                'push  rax',
            ]
        case ('div',):
            instructions += [
                'pop   rcx',
                'pop   rax',
                'cdq',
                'idiv  rcx',
                'push  rax',
            ]
        case ('load',):
            instructions += [
                'pop   rdx',
                'neg   rdx',
                'add   rdx, rbx',
                'mov   rax, [rdx]',
                'push  rax',
            ]
        case ('store',):
            instructions += [
                'pop   rdx',
                'neg   rdx',
                'add   rdx, rbx',
                'mov   rax, [rsp]',
                'mov   [rdx], rax',
            ]
        case _:
            raise NotImplementedError(ir)

    return instructions

def asm_to_obj(asm):
    pass


def obj_to_bin(obj):
    pass


def asm_to_bin(asm):
    pass


def ir_to_text(instructions):
    return '\n'.join([' '.join(inst) for inst in instructions])


def format_line(line):
    tab_width = 8
    l = ""
    if ':' in line:
        x = re.split(":", line, 1)
        l += f'{x[0] + ": ":<{tab_width}}'
        line = x[1]
    else:
        l += tab_width * ' '

    if line.startswith(";;;"):
        return l + line + '\n'

    comment = None
    if ";" in line:
        x = re.split(";", line.strip(), 1)
        comment = x[1]
        line = x[0]

    x = re.split(r"[\s]+", line.strip(), 1)
    l += f'{x[0]:<{tab_width}}'

    if len(x) > 1:
        line = x[1]
        x = re.split(",", line.strip())
        for y in x[:-1]:
            l += f'{y.strip() + ",":<{tab_width}}'
        l += f'{x[-1].strip():<{tab_width}}'
    if comment:
        l = f'{l:<40}' + ";" + comment

    return l + '\n'


def format_code(c):
    if type(c) == builtins.str:
        c = c.splitlines()

    return "".join([format_line(l) for l in c])


def output_text(args, text):
    if args.outfile == '-':
        print(text)
    else:
        with open(args.outfile, 'w') as f:
            f.write(text)
            f.write('\n')


def main(args):
    from_stage = 'src'
    to_stage = 'exe'

    match args.file.split('.'):
        case [*_, 'incc24']:
            from_stage = 'src'
        case [*_, 's']:
            from_stage = 'asm'
        case [*_, 'o']:
            from_stage = 'obj'
        case _:
            raise NotImplementedError("unknown file type")

    match args.outfile.split('.'):
        case [*_, 'cma']:
            to_stage = 'ir'
        case [*_, 's']:
            to_stage = 'asm'
        case [*_, 'o']:
            to_stage = 'obj'
        case [*_, 'exe']:
            to_stage = 'exe'
        case ['-']:
            pass
        case _:
            raise NotImplementedError("unknown file type")

    if args.emit is not None:
        to_stage = args.emit

    asm = None

    # provide source as text
    if from_stage == 'src':
        with open(args.file, 'r') as f:
            ast = parse_expr(f.read())

        # convert source to intermediate representation
        env = Environment()
        ir = code_r(ast, env)

    if to_stage == 'ir':
        output_text(args, ir_to_text(ir))
        return

    # provide assembly as text
    if from_stage == 'asm':
        asm_file = args.file
    elif ir is not None:
        # convert intermediate representation to assembly
        asm = x86_program(ir_to_asm(ir), env)

    if to_stage == 'asm':
        output_text(args, asm)
        return

    # provide object file
    if from_stage == 'obj':
        obj_file = args.file
    elif asm is not None:
        obj_file = args.outfile if to_stage == 'obj' else 'tmp.o'
        asm_file = 'tmp.s'
        with open(asm_file, 'w') as f:
            f.write(asm)
        subprocess.run(['nasm', '-g', '-F', 'dwarf', '-o', obj_file, '-f', 'elf64', asm_file], check=True)
        os.remove(asm_file)

    if to_stage == 'obj':
        return

    subprocess.run(['gcc', '-g', '-gdwarf', '-ggdb', '-z', 'noexecstack', '-no-pie', '-o', args.outfile, obj_file], check=True)

    if not from_stage == 'obj':
        os.remove(obj_file)