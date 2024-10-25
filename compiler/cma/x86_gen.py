import builtins

from compiler.cma.instruction import pop, loadc, operator, load, store, label, jump, jumpz, dup, swap, enter, alloc, \
    loadrc, ret, mark, call, slide

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
        case loadc(val):
            # language=nasm
            asm = f"""
                mov   rax, qword {val}
                push  rax
            """
        case pop():
            # language=nasm
            asm = """
                pop   rax
            """
        case dup():
            # language=nasm
            asm = """
                pop   rax
                push  rax
                push  rax
            """
        case swap():
            # language=nasm
            asm = """
                pop   rcx
                pop   rax
                push  rcx
                push  rax
            """
        case operator('neg' | 'inc' | 'dec' as op,):
            # language=nasm
            asm = f"""
                pop   rax
                {op_inst[op]:<5} rax
                push  rax
            """
        case operator('div' | 'mul' as op):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                {op:<5} rcx
                push  rax
            """
        case operator('le' | 'gr' | 'leq' | 'geq' | 'eq' | 'neq' as op):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                cmp   rax, rcx
                {op_inst[op]:<5} al
                movzx rax, al
                push rax
            """
        case operator(op):
            # language=nasm
            asm = f"""
                pop   rcx
                pop   rax
                {op_inst[op]:<5} rax, rcx
                push  rax
            """
        case load():
            # language=nasm
            asm = """
                pop   rdx
                neg   rdx
                add   rdx, rbx
                mov   rax, [rdx]
                push  rax
            """
        case store():
            # language=nasm
            asm = """
                pop   rdx
                neg   rdx
                add   rdx, rbx
                mov   rax, [rsp]
                mov   [rdx], rax
            """
        case label(name):
            # language=nasm
            asm = f"""
                {name}:
            """
        case jump(lbl):
            # language=nasm
            asm = f"""
                jmp   {lbl}
            """
        case jumpz(lbl):
            # language=nasm
            asm = f"""
                pop   rax
                test  rax, rax
                je    {lbl}
            """
        case enter():
            # language=nasm
            asm = f"""
                mov   rbp, rbx
                sub   rbp, rsp            
            """
        case alloc(size):
            # language=nasm
            asm = f"""
                sub   rsp, qword {size}            
            """
        case loadrc(offset):
            # language=nasm
            asm = f"""
                mov   rax, rbp
                add   rax, qword {offset}
                push  rax
            """
        case ret():
            # language=nasm
            asm = f"""
                mov   rsp, rbx             ; restore stack pointer to prev frame 
                sub   rsp, rbp             ; " rsp <- rbx - rbp (= N)
                mov   rax, rbx             ; restore frame pointer
                sub   rax, rbp             ; "
                mov   rbp, [rax+8]         ; " rbp <- [rbx - rbp + 8]
                ret
            """
        case mark():
            # language=nasm
            asm = f"""
                push  rbp
            """
        case call():
            # language=nasm
            asm = f"""
                pop   rax
                call  rax
            """
        case slide(discard, 8):
            # language=asm
            asm = f"""
                pop   rax
                add   rsp, qword {discard}
                push  rax
            """
        case _:
            raise NotImplementedError(ir)

    if type(ir) == label:
        return asm.strip() + '\n'

    return f';;; {ir}\n' + asm.strip() + '\n'