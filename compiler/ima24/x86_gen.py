import builtins

from compiler.util import format_code


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


def malloc(n):
    # language=nasm
    return f"""
        mov   rdi, 8*{n}
        call  malloc
        mov   rdx, rax
    """.strip()


def asm_gen(ir):
    if type(ir) == builtins.list:
        asm = ''
        for inst in ir:
            asm += asm_gen(inst)
        return asm

    match ir:
        case ('label', name):
            # language=nasm
            asm = f"""
                {name}:
            """

        case ('pop',):
            # language=nasm
            asm = f"""
                pop   rax
            """

        case ('dup',):
            # language=nasm
            asm = """
                push  qword [rsp]
            """

        case ('swap',):
            # language=nasm
            asm = """
                pop   rax
                pop   rcx
                push  rax
                push  rcx
            """

        case ('loadc', val):
            # language=nasm
            asm = f"""
                mov   rax, qword {val}
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

        case ('alloc', n):
            # language=nasm
            asm = f"""
                {malloc(2)}
                mov qword [rdx], 0
                mov qword [rdx + 1*8], 0
                push rdx""" * n

        case ('mkvec', n):
            asm = malloc(n + 1) + "\n".join([
                # language=nasm
                f"pop   qword [rdx + 8*(1 + {n - 1 - i})]" for i in range(n)
            ])
            # language=nasm
            asm += f"""
                mov   qword [rdx], {n}
                push  rdx
            """

        case ('setgp',):
            # language=nasm
            asm = f"""
                pop   r12
            """

        case ('pushglob', addr):
            # language=nasm
            asm = f"""
                push  qword [r12 + 8*(1 + {addr})]
            """

        case ('pushloc', addr):
            # language=nasm
            asm = f"""
                push  qword [rbp - 8*{addr}]
            """

        case ('slide', n):
            # language=nasm
            asm = f"""
                pop   rax
                add   rsp, 8*{n}
                push  rax
            """

        case ('mkind', t):
            # language=nasm
            asm = f"""
                {malloc(2)}
                pop   qword [rdx]
                mov   qword [rdx + 8*1], '{t}'
                push  rdx
            """

        case ('mkbasic',):
            # language=nasm
            asm = f"""
                {malloc(1)}
                pop   qword [rdx]
                push  rdx
            """

        case ('getbasic',):
            # language=nasm
            asm = f"""
                pop   rdx,
                mov   rdx, [rdx]
                push  qword [rdx]
            """

        case ('store',):
            # language=nasm
            asm = f"""
                pop   rdx
                mov   rcx, [rsp]
                mov   rax, [rdx]
                mov   [rcx], rax
                mov   rax, [rdx + 8*1]
                mov   [rcx + 8*1], rax
            """

        case ('jump', label):
            # language=nasm
            asm = f"""
                jmp   {label}
            """

        case ('jumpz', label):
            # language=nasm
            asm = f"""
                pop   rax
                test  rax, rax
                je    {label}
            """

        case _:
            raise NotImplementedError(ir)

    if ir[0] == 'label':
        return asm.strip() + '\n'

    return f';;; {ir}\n' + asm.strip() + '\n'


def x86_program(x86_code, env):
    # language=nasm
    return f"""
    extern  printf, malloc
SECTION .data               ; Data section, initialized variables
i64_fmt:db  "%lld", 10, 0 ; printf format for printing an int64

SECTION  .text
global main
main:
        enter 0, 0
{format_code(x86_code)}
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
"""