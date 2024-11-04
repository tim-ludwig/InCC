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
