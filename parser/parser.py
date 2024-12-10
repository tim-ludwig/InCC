# type: ignore
# ignore name conflict
from ply import yacc
from lexer.lexer import tokens, lexer, make_incc24_lexer

from parser.literals import *
from parser.operators import *
from parser.variables import *
from parser.sequences import *
from parser.controlflow import *
from parser.functions import *
from parser.struct import *
from parser.module import *


precedence = [
    ['nonassoc', 'THEN'],
    ['nonassoc', 'ELSE', 'DO', 'WHILE', 'IN'],
    ['left', 'COMMA'],
    ['right', 'ASSIGN'],
    ['right', 'RIGHT_ARROW'],
    ['left', 'OR', 'NOR', 'XOR'],
    ['left', 'IMP'],
    ['left', 'AND', 'NAND'],
    ['left', 'EQS', 'NEQS', 'EQ', 'NEQ'],
    ['left', 'LT', 'GT', 'LE', 'GE'],
    ['left', 'PLUS', 'MINUS'],
    ['left', 'TIMES', 'DIVIDE'],
    ['right', 'NOT', 'UMINUS', 'UPLUS'],
    ['right', 'LPAREN', 'LBRACKET', 'DOT'],
]


def p_program(p):
    """
    program : expression
    """
    p[0] = Program(p.linespan(0), p[1])


def p_error(p):
    raise SyntaxError(f"Syntax error at token {p}")


def p_trap(p):
    """
    expression : TRAP
    """
    p[0] = TrapExpression(p.linespan(0))


parser = yacc.yacc(start='program')


def parse_expr(text: str) -> Expression:
    return parser.parse(input=text, lexer=make_incc24_lexer(), tracking=True)


def parse_file(path: str) -> Expression:
    def annotate_file(expr, path):
        expr.position = (path, *expr.position)

        match expr:
            case NumberLiteral(_, value): pass
            case BoolLiteral(_, value): pass
            case StringLiteral(_, value): pass
            case CharLiteral(_, value): pass
            case ArrayLiteral(_, elements):
                for elem in elements:
                    annotate_file(elem, path)
            case DictLiteral(_, elements):
                for key, value in elements:
                    annotate_file(key, path)
                    annotate_file(value, path)

            case UnaryOperatorExpression(_, operator, operand):
                annotate_file(operand, path)

            case BinaryOperatorExpression(_, operator, operands):
                annotate_file(operands[0], path)
                annotate_file(operands[1], path)

            case AssignExpression(_, var, expression):
                annotate_file(var, path)
                annotate_file(expression, path)

            case VariableExpression(_, name): pass

            case LockExpression(_, _, body):
                annotate_file(body, path)

            case LocalExpression(_, assignments, body):
                for assignment in assignments:
                    annotate_file(assignment, path)
                annotate_file(body, path)

            case SequenceExpression(_, expressions):
                for expression in expressions:
                    annotate_file(expression, path)

            case LoopExpression(_, count, body):
                annotate_file(count, path)
                annotate_file(body, path)

            case WhileExpression(_, condition, body):
                annotate_file(condition, path)
                annotate_file(body, path)

            case DoWhileExpression(_, condition, body):
                annotate_file(condition, path)
                annotate_file(body, path)

            case IfExpression(_, condition, then_body, else_body):
                annotate_file(condition, path)
                annotate_file(then_body, path)
                if else_body: annotate_file(else_body, path)

            case LambdaExpression(_, arg_names, body, rest_args):
                annotate_file(body, path)

            case ProcedureExpression(_, arg_names, local_names, body):
                annotate_file(body, path)

            case CallExpression(_, f, arg_exprs):
                for arg_expr in arg_exprs:
                    annotate_file(arg_expr, path)
                annotate_file(f, path)

            case StructExpression(_, initializers, parent_expr):
                if parent_expr: annotate_file(parent_expr, path)
                for initializer in initializers:
                    annotate_file(initializer, path)

            case MemberAccessExpression(_, expr, member, up_count):
                annotate_file(expr, path)

            case MemberAssignExpression(_, member, expr):
                annotate_file(expr, path)

            case ThisExpression(_): pass
            case ImportExpression(_, path): pass
            case TrapExpression(_): pass
            case _:
                raise NotImplementedError(expr)

    with open(path) as f:
        try:
            expr = parse_expr(f.read())
            annotate_file(expr, path)
            return expr
        except SyntaxError as e:
            raise SyntaxError(e.msg + " in " + path)