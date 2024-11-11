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
    """


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
        case ('mkbasic',):
            # language=nasm
            asm = f"""
                {malloc(2)}
                mov   qword [rdx], 'B'
                pop   qword [rdx + 8*1]
                push  rdx
            """
        case ('slide', discard):
            # language=nasm
            asm = f"""
                pop   rax
                add   rsp, 8*{discard}
                push  rax
            """
        case ('pushloc', offset):
            # language=nasm
            asm = f"""
                push  qword [rsp + 8*{offset}]
            """

        case ('pushglob', offset):
            # language=nasm
            asm = f"""
                push  qword [rbx + 8*(2 + {offset})]
            """
        case ('getbasic',):
            # language=nasm
            asm = f"""
                pop   rdx
                mov   rax, [rdx + 8*1]
                push  rax
            """
        case ('mkvec', n):
            asm = malloc(n + 2) + "\n".join([
                # language=nasm
                f"pop   qword [rdx + 8*(2 + {n - 1 - i})]" for i in range(n)
            ])
            # language=nasm
            asm += f"""
                mov   qword [rdx + 8*1], {n}
                mov   qword [rdx], 'V'
                push  rdx
            """

        case ('mkfunval', addr):
            # language=nasm
            asm = f"""
                {malloc(4)}
                mov   qword [rdx], 'F'
                mov   qword [rdx + 8*1], {addr}
                mov   qword [rdx + 8*2], 0
                pop   qword [rdx + 8*3]
                push  rdx
            """

        case ('popenv',):
            # language=nasm
            asm = f"""
                mov   rbx, [rbp + 8*2]
                pop   qword [rbp + 8*2]
                lea   rsp, [rbp + 8*2]
                mov   rax, [rbp]
                mov   rbp, [rbp + 8*1]
                jmp   rax
            """

        case ('mark', ret):
            # language=nasm
            asm = f"""
                push  rbx
                push  rbp
                lea   rax, [rel {ret}]
                push  rax
                mov   rbp, rsp
            """

        case ('apply',):
            # language=nasm
            asm = f"""
                pop   rdx
                mov   rbx, [rdx + 8*3]
                mov   rax, [rdx + 8*1]
                jmp   rax
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