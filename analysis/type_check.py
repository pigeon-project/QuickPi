from typing import Union, Dict, Tuple, Optional
import ast as xast
from ast import AST

from .mata_info import TypeInfo, NameSpace, Module, Function
from .utils import Name, PosInfo, AnalysisError

def create_type(texpr: xast.expr) -> TypeInfo:
    raise NotImplementedError()


def create_function(
    ctx: NameSpace,
    ast: Union[xast.FunctionDef, xast.AsyncFunctionDef]) -> Function:
    is_async = False
    if isinstance(ast, xast.AsyncFunctionDef):
        is_async = True

    def get_function_args(ctx: Function, args: xast.arguments) -> Dict[Name, TypeInfo]:
        def get_arg_type(ctx: Function, t: Optional[xast.expr]) -> TypeInfo:
            if t: return create_type(t)
            # create typevar
            raise NotImplementedError()
        return {i.arg: get_arg_type(ctx, i.annotation) for i in args.args}

    def get_function_return_type(ctx: Function, args: Optional[xast.expr]) -> TypeInfo:
        if args is None:
            # create typevar
            pass
        else:
            # create typevar
            pass
        raise NotImplementedError()

    functx = Function(
            PosInfo(ast.lineno, ast.col_offset),
            ast.name, f'',
            is_async, is_pure=None,
            params={},
            return_type=None,
            throw=None,
            sub_namespace=None,
            body=ast.body,
            parent=ctx, top_level=ctx.get_top_level())
    functx.params = get_function_args(functx, ast.args)
    functx.return_type = get_function_return_type(functx, ast.returns)
    return functx

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