from typing import Union, Dict, Tuple, Optional
import ast
from functools import singledispatch

from utils import Name, PosInfo, AnalysisError, AnalysisWarning
from meta_info import NameSpace, Module, Function, TypeInfo, TypeRef
from create_tools import create_function



@singledispatch
def infer(ctx: NameSpace, inp: ast.AST) -> TypeInfo:
    raise AnalysisError(
        'Invalid input',
        PosInfo(inp.lineno, inp.col_offset),
        top_level=ctx.get_top_level())


@infer.register
def _(ctx: NameSpace, inp: ast.BoolOp) -> TypeInfo:
    ...


@singledispatch
def check(ctx: NameSpace, inp: ast.AST):
    raise AnalysisError(
        'Invalid input',
        PosInfo(inp.lineno, inp.col_offset),
        top_level=ctx.get_top_level())


@check.register
def check_expr(ctx: NameSpace, inp: ast.Expr):
    rt: TypeInfo = infer(inp.value)
    try:
        unify(rt, TypeRef('Unit').get_true_type())
    except TypeNonUnifyError:
        print(AnalysisWarning(
            '[unify error]: Type is non unify',
            PosInfo(inp.lineno, inp.col_offset), 
            ctx.get_top_level()))



# @check.register
def stmt_check_in_module(ctx: Module, inp: ast.stmt) -> NameSpace:
    if isinstance(ast, ast.FunctionDef) or isinstance(ast, ast.AsyncFunctionDef):
        functx = create_function(ctx, ast)
    return ctx

def module_check(ctx: Module, inp: ast.AST) -> Module:
    if isinstance(ast, ast.Module):
        for i in ast.body:
            pass
        return ctx
    raise AnalysisError(
            '[context error]: module_check context is not module',
            PosInfo(inp.lineno, inp.col_offset),
            ctx.get_top_level())