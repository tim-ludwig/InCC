import os
import subprocess

from compiler.cma.ir_gen import code_r as cma_code_r
from compiler.cma.x86_gen import x86_program as cma_x86_program, asm_gen as cma_asm_gen
from compiler.mama.ir_gen import code_b as mama_code_b
from compiler.mama.x86_gen import x86_program as mama_x86_program, asm_gen as mama_asm_gen
from compiler.ima24.ir_gen import code_b as ima24_code_b
from compiler.ima24.x86_gen import x86_program as ima24_x86_program, asm_gen as ima24_asm_gen

from compiler.util import format_code
from environment import Environment
from parser.parser import parse_expr


def ast_to_ir(ast, vm):
    env = Environment()
    match vm:
        case 'cma':
            return cma_code_r(ast, env), env, None
        case 'mama':
            return mama_code_b(ast, env, 0), env, None
        case 'ima24':
            lb = dict()
            return ima24_code_b(ast, env, 0, lb), env, lb


def ir_to_asm(ir, env, lb, vm):
    match vm:
        case 'cma':
            return cma_x86_program(cma_asm_gen(ir), env)
        case 'mama':
            return mama_x86_program(mama_asm_gen(ir), env)
        case 'ima24':
            return ima24_x86_program(ima24_asm_gen(ir), env, lb)


def asm_to_obj(asm_file, obj_file):
    res = subprocess.run(['nasm', '-g', '-F', 'dwarf', '-o', obj_file, '-f', 'elf64', asm_file])
    return res.returncode


def obj_to_bin(obj_file, bin_file):
    res = subprocess.run(['gcc', '-g', '-gdwarf', '-ggdb', '-z', 'noexecstack', '-no-pie', '-o', bin_file, obj_file])
    return res.returncode


def ir_to_text(instructions):
    lines = []
    for inst in instructions:
        match inst:
            case ('label', name):
                line = f'{name}:'
            case (mnemonic,):
                line = f'    {mnemonic}'
            case (mnemonic, *args):
                line = f'    {mnemonic:<8}{", ".join(map(str, args))}'
            case str():
                line = inst
        lines.append(line)

    return '\n'.join(lines)


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
        case [*_, 'cma' | 'mama']:
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
        ir, env, lb = ast_to_ir(ast, args.vm)

    if to_stage == 'ir':
        output_text(args, ir_to_text(ir))
        return

    # provide assembly in file
    if from_stage == 'asm':
        asm_file = args.file
    elif ir is not None:
        # convert intermediate representation to assembly
        asm = ir_to_asm(ir, env, lb, args.vm)

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
