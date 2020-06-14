from typing import Union, Dict, List, Tuple, Optional
import ast as xast
from ast import AST

from .mata_info import TypeInfo, NameSpace, Module, Function, TypeVar, TypeRef
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
    return TypeVar(is_assign=False)


# create function


def get_function_args(ctx: Function, args: xast.arguments) -> Dict[Name, TypeInfo]:
    assert not args.vararg
    assert not args.kwonlyargs
    assert not args.kw_defaults
    assert not args.kwarg
    assert not args.defaults
    return {i.arg: create_any_type(ctx, i.annotation) for i in args.args}

def exist_forall(i: xast.expr) -> bool:
    if isinstance(i, xast.Call):
        if isinstance(i.func, xast.Name):
            if i.func == 'forall':
                return True
    return False

def forall_detail(inp: List[xast.expr]) -> Optional[List[TypeVar]]:
    r: List[TypeVar] = []
    for i in inp:
        if isinstance(i, xast.Name):
            r.append(TypeVar(is_assign=True, name=i.id))
        else:
            return None
    return r    


def create_function(
    ctx: NameSpace,
    ast: Union[xast.FunctionDef, xast.AsyncFunctionDef]) -> Function:
    is_async = False
    if isinstance(ast, xast.AsyncFunctionDef):
        is_async = True

    r: List[xast.expr] = list(filter(exist_forall, ast.decorator_list))
    # 判断有且只有一个forall
    assert len(r) == 1
    # 检查是否有多余的装饰器
    assert len(r) == len(ast.decorator_list)
    def fuck_mypy(i: xast.expr) -> xast.Call:
        if isinstance(i, xast.Call):
            return i
        assert False
    r1: List[xast.Call] = [fuck_mypy(i) for i in r]
    r2 = forall_detail(r1[0].args)
    type_vars: List[TypeVar] = []
    if r2:
        type_vars = r2

    functx = Function(
            PosInfo(ast.lineno, ast.col_offset),
            ast.name, f'',
            is_async, is_pure=None,
            type_vars=type_vars,
            params={},
            return_type=None,
            throw=None,
            sub_namespace=None,
            body=ast.body,
            parent=ctx, top_level=ctx.get_top_level())
    functx.params = get_function_args(functx, ast.args)
    functx.return_type = create_any_type(functx, ast.returns)
    return functx