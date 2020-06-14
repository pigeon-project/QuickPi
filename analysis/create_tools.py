from typing import Union, Dict, Tuple, Optional
import ast as xast
from ast import AST

from .mata_info import TypeInfo, NameSpace, Module, Function
from .utils import Name, PosInfo, AnalysisError


# create type

def create_type(ctx: NameSpace, texpr: xast.expr) -> TypeInfo:
    if isinstance(texpr, xast.Name):
        # TODO: create type name ref
        pass
    if isinstance(texpr, xast.BinOp):
        # TODO:
        pass
    raise NotImplementedError()

def create_any_type(ctx: NameSpace, texpr: Optional[xast.expr]) -> TypeInfo:
    if texpr:
        return create_type(ctx, texpr)
    # TODO: create typevar
    raise NotImplementedError()


# create function


def get_function_args(ctx: Function, args: xast.arguments) -> Dict[Name, TypeInfo]:
    assert not args.vararg
    assert not args.kwonlyargs
    assert not args.kw_defaults
    assert not args.kwarg
    assert not args.defaults
    return {i.arg: create_any_type(ctx, i.annotation) for i in args.args}


def create_function(
    ctx: NameSpace,
    ast: Union[xast.FunctionDef, xast.AsyncFunctionDef]) -> Function:
    is_async = False
    if isinstance(ast, xast.AsyncFunctionDef):
        is_async = True

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
    functx.return_type = create_any_type(functx, ast.returns)
    return functx