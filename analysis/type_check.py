# import ast
from ast import AST, Num, Str, expr, Bytes, Call, stmt, AnnAssign, BoolOp, And, Or, Not

from .mata_info import Context
from .type_info import TypeInfo, TypeRef, builtin_bool, builtin_bytes, builtin_float, builtin_int, builtin_str

macig_method_map = {
    And: '__and__',
    Or: '__or__',
    Not: '__not__',
}

def type_assert(ast: AST, type: TypeInfo):
    pass


def expr_infer(context: Context, ast: expr) -> TypeInfo:
    if isinstance(ast, Str):
        return builtin_str
    if isinstance(ast, Num):
        if isinstance(ast.n, int):
            return builtin_int
        if isinstance(ast.n, float):
            return builtin_float
        assert False
    if isinstance(ast, Bytes):
        return builtin_bytes
    if isinstance(ast, BoolOp):
        # Python 魔方方法能定制操作符行为。这套行不通
        left_type = type_infer(context, ast.values[0])
        if isinstance(left_type, TypeRef):
            left_type_info = left_type.get_true_type(context)
            fun_info = left_type_info.find_method(macig_method_map[ast.op])
        else:
            raise RuntimeError('喵喵喵喵喵？')
        # left_type.
        # type_assert(ast.values[0], builtin_bool)
        # type_assert(ast.values[1], builtin_bool)
        return builtin_bool
    # if isinstance(ast, Call):
    #     return TypeRef('bytes', 'qpy.builtin.bytes')


def type_infer(context: Context, ast: AST) -> TypeInfo:
    if isinstance(ast, expr):
        return expr_infer(context, ast)
    # if isinstance(ast, )

    pass


def annassign_check(context: Context, ast: AnnAssign):
    pass


def statement_check(context: Context, ast: stmt):
    if isinstance(ast, AnnAssign):
        return annassign_check(context, ast)
    pass


def type_check(context: Context, ast: AST):
    if isinstance(ast, stmt):
        return statement_check(context, ast)
    # type_infer(context, ast)
