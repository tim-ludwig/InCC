import builtins
import re

from syntaxtree.controlflow import IfExpression, WhileExpression, LoopExpression, DoWhileExpression, RepeatExpression
from syntaxtree.functions import LambdaExpression, CallExpression, ReturnExpression, QuitExpression
from syntaxtree.literals import NumberLiteral
from syntaxtree.operators import UnaryOperatorExpression, BinaryOperatorExpression
from syntaxtree.sequences import SequenceExpression
from syntaxtree.variables import AssignExpression, VariableExpression, LocalExpression


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


label_count = dict()
def make_unique_label(*label):
    if len(label) > 1:
        return [make_unique_label(l) for l in label]

    label = label[0]

    global label_count
    label_count[label] = label_count.get(label, 0) + 1
    return label + str(label_count[label] - 1)


def free_vars(expr):
    match expr:
        case NumberLiteral(_, _):
            return set()

        case UnaryOperatorExpression(_, _, operand):
            return free_vars(operand)

        case BinaryOperatorExpression(_, _, (left, right)):
            return free_vars(left) | free_vars(right)

        case AssignExpression(_, var, expression):
            return  free_vars(var) | free_vars(expression)

        case VariableExpression(_, name):
            return {name}

        case IfExpression(_, condition, then_body, else_body):
            return free_vars(condition) | free_vars(then_body) | free_vars(else_body)

        case LocalExpression(_, assignments, body):
            return free_vars(body) - {assignment.var.name for assignment in assignments}

        case LambdaExpression(_, arg_names, body, _):
            return free_vars(body) - set(arg_names)

        case CallExpression(_, f, args):
            return free_vars(f) | {v for arg in args for v in free_vars(arg)}

        case ReturnExpression(_, val) | QuitExpression(_, val):
            return free_vars(val)

        case SequenceExpression(_, expressions):
            return {v for expr in expressions for v in free_vars(expr)}

        case IfExpression(_, condition, then_expr, else_expr):
            return free_vars(condition) | free_vars(then_expr) | free_vars(else_expr)

        case WhileExpression(_, c, body) | LoopExpression(_, c, body) | DoWhileExpression(_, c, body):
            return free_vars(c) | free_vars(body)

        case RepeatExpression(_, body):
            return free_vars(body)

        case None:
            return set()

        case _:
            raise NotImplementedError(expr)
