import builtins

from compiler.x86_util import format_code

op_inst = {
    'neg': 'neg',
    'inc': 'inc',
    'dec': 'dec',
    'add': 'add',
    'sub': 'sub',
    'mul': 'imul',
    'div': 'idiv',
    'le': 'setl',
    'gr': 'setg',
    'leq': 'setle',
    'geq': 'setge',
    'eq': 'sete',
    'neq': 'setne',
}

def asm_gen(ir):
    if type(ir) == builtins.list:
        asm = ''
        for inst in ir:
            asm += asm_gen(inst)
        return asm

    match ir:
        case ('loadc', val):
            # language=nasm
            asm = f"""
                mov   rax, qword {val}
                push  rax
            """
        case ('pop', ):
            # language=nasm
            asm = """
                pop   rax
            """
        case ('dup', ):
            # language=nasm
            asm = """
                pop   rax
                push  rax
                push  rax
            """
        case ('swap', ):
            # language=nasm
            asm = """
                pop   rcx
                pop   rax
                push  rcx
                push  rax
            """
        case ('neg' | 'inc' | 'dec' as op, ):
            # language=nasm
            asm = f"""
                pop   rax
                {op_inst[op]:<5} rax
                push  rax
            """
        case ('div' | 'mul' as op, ):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                cdq
                {op_inst[op]:<5} rcx
                push  rax
            """
        case ('le' | 'gr' | 'leq' | 'geq' | 'eq' | 'neq' as op, ):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                cmp   rax, rcx
                {op_inst[op]:<5} al
                movzx rax, al
                push rax
            """
        case ('add' | 'sub' as op, ):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                {op_inst[op]:<5} rax, rcx
                push  rax
            """
        case ('label', name):
            # language=nasm
            asm = f"""
                {name}:
            """
        case ('jump', lbl):
            # language=nasm
            asm = f"""
                jmp   {lbl}
            """
        case ('jumpz', lbl):
            # language=nasm
            asm = f"""
                pop   rax
                test  rax, rax
                je    {lbl}
            """
        case _:
            raise NotImplementedError(ir)

    if ir[0] == 'label':
        return asm.strip() + '\n'

    return f';;; {ir}\n' + asm.strip() + '\n'


def x86_prefix(env):
    # language=nasm
    return """
        extern  printf, malloc
        SECTION .data               ; Data section, initialized variables
        i64_fmt:  db  "%lld", 10, 0 ; printf format for printing an int64 
    """


def x86_start(env):
    # language=nasm
    return format_code(f"""
        SECTION  .text
        global main
        main:
          enter 0, 0
    """)


def x86_final(env):
    # language=nasm
    return format_code(f"""
          pop   rax
          mov   rsi, rax
          mov   rdi,i64_fmt         ; arguments in rdi, rsi
          mov   rax,0               ; no xmm registers used
          push  rbp                 ; set up stack frame, must be alligned
          call  printf              ; Call C function
          pop   rbp                 ; restore stack
          ;;; Rueckkehr zum aufrufenden Kontext
          pop   rbp                 ; original rbp ist last thing on the stack
          mov   rax,0               ; return 0
          ret
    """)


def x86_program(x86_code, env) :
    program  = x86_prefix(env)
    program += x86_start(env)
    program += "\n;;; Start des eigentlichen Programms\n"
    program += format_code(x86_code)
    program += ";;; Ende des eigentlichen Programms\n\n"
    program += x86_final(env)
    return program