from _ast import AST

from .mata_info import Context
from .type_info import TypeInfo


def type_infer(_context: Context, _ast: AST) -> TypeInfo:
    pass


def type_check(context: Context, ast: AST):
    type_infer(context, ast)
    pass
