import os
import subprocess

from compiler.cma.ir_gen import code_r
from compiler.cma.x86_gen import asm_gen
from compiler.x86_util import x86_program, format_code
from environment import Environment
from parser.parser import parse_expr


def ast_to_ir(ast):
    env = Environment()
    return code_r(ast, env), env


def ir_to_asm(ir, env):
    return x86_program(asm_gen(ir), env)


def asm_to_obj(asm_file, obj_file):
    res = subprocess.run(['nasm', '-g', '-F', 'dwarf', '-o', obj_file, '-f', 'elf64', asm_file])
    return res.returncode


def obj_to_bin(obj_file, bin_file):
    res = subprocess.run(['gcc', '-g', '-gdwarf', '-ggdb', '-z', 'noexecstack', '-no-pie', '-o', bin_file, obj_file])
    return res.returncode


def ir_to_text(instructions):
    return '\n'.join([str(inst) for inst in instructions])


def output_text(args, text):
    if args.outfile == '-':
        print(text)
    else:
        with open(args.outfile, 'w') as f:
            f.write(text)
            f.write('\n')


def main(args):
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

    # provide source as text
    if from_stage == 'src':
        with open(args.file, 'r') as f:
            ast = parse_expr(f.read())

        # convert source to intermediate representation
        ir, env = ast_to_ir(ast)

    if to_stage == 'ir':
        output_text(args, format_code(ir_to_text(ir)))
        return

    # provide assembly in file
    if from_stage == 'asm':
        asm_file = args.file
    elif ir is not None:
        # convert intermediate representation to assembly
        asm = ir_to_asm(ir, env)

        if to_stage == 'asm':
            output_text(args, asm)
            return

        asm_file = 'tmp.s'
        with open(asm_file, 'w') as f:
            f.write(asm)

    # provide object file
    if from_stage == 'obj':
        obj_file = args.file
    elif asm_file is not None:
        obj_file = args.outfile if to_stage == 'obj' else 'tmp.o'

        res = asm_to_obj(asm_file, obj_file)

        if from_stage != 'asm' and not args.keep_asm:
            os.remove(asm_file)

        if res != 0:
            return

    if to_stage == 'obj':
        return

    res = obj_to_bin(obj_file, args.outfile)

    if from_stage != 'obj':
        os.remove(obj_file)

    if res != 0:
        return
