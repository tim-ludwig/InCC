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
        case ('pop',):
            # language=nasm
            asm = """
                pop   rax
            """
        case ('dup',):
            # language=nasm
            asm = """
                pop   rax
                push  rax
                push  rax
            """
        case ('swap',):
            # language=nasm
            asm = """
                pop   rcx
                pop   rax
                push  rcx
                push  rax
            """
        case ('neg' | 'inc' | 'dec' as op,):
            # language=nasm
            asm = f"""
                pop   rax
                {op_inst[op]:<5} rax
                push  rax
            """
        case ('div' | 'mul' as op,):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                cdq
                {op:<5} rcx
                push  rax
            """
        case ('le' | 'gr' | 'leq' | 'geq' | 'eq' | 'neq' as op,):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                cmp   rax, rcx
                {op_inst[op]:<5} al
                movzx rax, al
                push rax
            """
        case ('add' | 'sub' as op,):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                {op_inst[op]:<5} rax, rcx
                push  rax
            """
        case ('load',):
            # language=nasm
            asm = """
                pop   rdx
                neg   rdx
                add   rdx, rbx
                mov   rax, [rdx]
                push  rax
            """
        case ('store',):
            # language=nasm
            asm = """
                pop   rdx
                neg   rdx
                add   rdx, rbx
                mov   rax, [rsp]
                mov   [rdx], rax
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
        case ('enter',):
            # language=nasm
            asm = f"""
                mov   rbp, rbx
                sub   rbp, rsp            
            """
        case ('alloc', size):
            # language=nasm
            asm = f"""
                sub   rsp, qword {size}            
            """
        case ('loadrc', offset):
            # language=nasm
            asm = f"""
                mov   rax, rbp
                add   rax, qword {offset}
                push  rax
            """
        case ('ret',):
            # language=nasm
            asm = f"""
                mov   rsp, rbx             ; restore stack pointer to prev frame 
                sub   rsp, rbp             ; " rsp <- rbx - rbp (= N)
                mov   rax, rbx             ; restore frame pointer
                sub   rax, rbp             ; "
                mov   rbp, [rax+8]         ; " rbp <- [rbx - rbp + 8]
                ret
            """
        case ('mark',):
            # language=nasm
            asm = f"""
                push  rbp
            """
        case ('call',):
            # language=nasm
            asm = f"""
                pop   rax
                call  rax
            """
        case ('slide', discard, 8):
            # language=asm
            asm = f"""
                pop   rax
                add   rsp, qword {discard}
                push  rax
            """
        case _:
            raise NotImplementedError(ir)

    if ir[0] == 'label':
        return asm.strip() + '\n'

    return f';;; {ir}\n' + asm.strip() + '\n'


def x86_prefix(env):
    # language=nasm
    return """
        extern  printf
        SECTION .data               ; Data section, initialized variables
        i64_fmt:  db  "%lld", 10, 0 ; printf format for printing an int64 
    """


def x86_start(env):
    # language=nasm
    return format_code(f"""
        SECTION  .text
        global main
        main:
          push  rbp                 ; unnötig, weil es den Wert 1 enthält, trotzem notwendig, weil sonst segfault
          mov   rbx,rsp             ; store start of CMa stack in rbx
          sub   rbx,8               ; " 
          sub   rsp,{env.total_size():<16}; Platz für globale Variablen
          mov   rax,rsp             ; rsp zeigt auf den geretteten rbp
          sub   rax,qword 8         ; neuer rbp sollte ein wort darüber liegen
          mov   rbp,rax             ; set frame pointer to current (empty) stack pointer
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
          add   rsp,{env.total_size()}
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