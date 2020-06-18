from typing import Union, Dict, Tuple, Optional
import ast
from functools import singledispatch

from utils import Name, PosInfo, AnalysisError, AnalysisWarning
from meta_info import NameSpace, Module, Function, TypeInfo, TypeRef
from create_tools import create_function

@singledispatch
def load(ctx: NameSpace, inp: ast.FunctionDef):
    assert False


@load.register
def load_function(ctx: NameSpace, inp: ast.FunctionDef):
    functx = create_function(ctx, inp)
    ctx.register_name(functx.name, functx)


@load.register
def check_async_function_from_global(ctx: Module, inp: ast.AsyncFunctionDef):
    functx = create_function(ctx, inp)
    ctx.register_name(functx.name, functx)


@load.register
def check_async_function(ctx: Function, inp: ast.AsyncFunctionDef):
    assert ctx.is_async == True
    functx = create_function(ctx, inp)
    ctx.register_name(functx.name, functx)
