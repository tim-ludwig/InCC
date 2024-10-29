import builtins
import re


def format_line(line):
    line = line.strip()
    tab_width = 8
    l = ""
    if ':' in line:
        x = re.split(":", line, 1)
        l += f'{x[0] + ": ":<{tab_width}}'
        line = x[1]
    else:
        l += tab_width * ' '

    if line.startswith(";;;"):
        return (tab_width // 2) * ' ' + line + '\n'

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
