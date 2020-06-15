from typing import Union, Dict, Tuple, Optional
import ast as xast
from ast import AST

from utils import Name, PosInfo, AnalysisError
from mata_info import TypeInfo, NameSpace, Module, Function
from create_tools import create_function


def expr_check(ctx: NameSpace, ast: xast.expr) -> NameSpace:
    pass

def stmt_check(ctx: NameSpace, ast: xast.stmt) -> NameSpace:
    pass

def stmt_check_in_module(ctx: Module, ast: xast.stmt) -> NameSpace:
    if isinstance(ast, xast.FunctionDef) or isinstance(ast, xast.AsyncFunctionDef):
        functx = create_function(ctx, ast)
        pass
    return ctx

def module_check(ctx: Module, ast: xast.AST) -> Module:
    if isinstance(ast, xast.Module):
        for i in ast.body:
            pass
        return ctx
    raise AnalysisError(
            '[context error]: module_check context is not module',
            PosInfo(ast.lineno, ast.col_offset),
            ctx.get_top_level())