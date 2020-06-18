from typing import List, Optional, Union, Any
from enum import Enum
import ast

import meta_info as mi
from meta_info import NameSpace
from bytecode import ByteCode
from utils import trait, PosInfo


def from_arguments_to_arg(inp: ast.arguments) -> List[arg]:
    assert not inp.vararg
    assert not inp.kwonlyargs
    assert not inp.kw_defaults
    assert not inp.kwarg
    assert not inp.defaults
    return [arg(i) for i in inp.args]

@trait
class XAST:
    pos: PosInfo

    def __init__(self, inp: ast.AST):
        self.pos = PosInfo(inp.lineno, inp.col_offset)
    def type_check(self, ctx: NameSpace): ...
    # def codegen(self, ctx: strSpace) -> ByteCode: ...


class Module(XAST):
    body: List[stmt]
    # ctx: mi.Module

    def __init__(self, inp: ast.Module):
        super().__init__(inp)
        self.body = [stmt.create(i) for i in inp.body]


class stmt(XAST):
    @staticmethod
    def create(inp: ast.stmt) -> stmt:
        ...
    @staticmethod
    def create_list(inp: List[ast.stmt]) -> List[stmt]:
        return [stmt.create(i) for i in inp]


class FunctionDef(stmt):
    is_async: bool
    str: str
    args: List[arg]
    body: List[stmt]
    decorator_list: List[expr]
    returns: Optional[expr]

    def __init__(self, inp: Union[ast.FunctionDef, ast.AsyncFunctionDef]):
        super().__init__(inp)
        self.is_async = isinstance(inp, ast.AsyncFunctionDef)
        self.str = inp.name
        self.args = from_arguments_to_arg(inp.args)
        self.body = stmt.create_list(inp.body)
        self.decorator_list = expr.create_list(inp.decorator_list)
        self.returns = None if inp.returns is None else expr.create(inp.returns)

class ClassDef(stmt):
    str: str
    bases: List[expr]
    body: List[stmt]
    decorator_list: List[expr]

    def __init__(self, inp: ast.ClassDef):
        super().__init__(inp)
        self.str = inp.name
        # FIXME: check trait
        self.bases = expr.create_list(inp.bases)
        self.body = stmt.create_list(inp.body)
        self.decorator_list = expr.create_list(inp.decorator_list)


class Return(stmt):
    value: Optional[expr]

    def __init__(self, inp: ast.Return):
        super().__init__(inp)
        self.value = None if inp.value is None else expr.create(inp.value)


class Delete(stmt):
    targets: List[expr]

    def __init__(self, inp: ast.Delete):
        super().__init__(inp)
        self.value = expr.create_list(inp.targets)


class Assign(stmt):
    targets: List[expr]
    value: expr

    def __init__(self, inp: ast.Assign):
        super().__init__(inp)
        self.targets = expr.create_list(inp.targets)
        self.value = expr.create(inp.value)

class AugAssign(stmt):
    target: expr
    op: operator
    value: expr

    def __init__(self, inp: ast.AugAssign):
        super().__init__(inp)
        self.target = expr.create(inp.target)
        self.value = expr.create(inp.value)
        self.op = operator(inp.op)


class AnnAssign(stmt):
    target: expr
    annotation: expr
    value: Optional[expr]
    simple: int

    def __init__(self, inp: ast.AnnAssign):
        super().__init__(inp)
        self.target = expr.create(inp.target)
        self.annotation = expr.create(inp.annotation)
        self.value = None if inp.value is None else expr.create(inp.value)
        # self.simple = inp.simple
        # TODO: What is inp.simple ?
        # 小小的眼里有着大大的问号


class For(stmt):
    target: expr
    iter: expr
    body: List[stmt]
    orelse: List[stmt]
    
    def __init__(self, inp: ast.For):
        super().__init__(inp)
        self.target = expr.create(inp.target)
        self.iter = expr.create(inp.iter)
        self.body = stmt.create_list(inp.body)
        self.orelse = stmt.create_list(inp.orelse)


class AsyncFor(stmt):
    target: expr
    iter: expr
    body: List[stmt]
    orelse: List[stmt]
    
    def __init__(self, inp: ast.AsyncFor):
        super().__init__(inp)
        self.target = expr.create(inp.target)
        self.iter = expr.create(inp.iter)
        self.body = stmt.create_list(inp.body)
        self.orelse = stmt.create_list(inp.orelse)


class While(stmt):
    test: expr
    body: List[stmt]
    orelse: List[stmt]

    def __init__(self, inp: ast.While):
        # TODO: raise InvalidExprError
        super().__init__(inp)
        self.test = expr.create(inp.test)
        self.body = stmt.create_list(inp.body)
        self.orelse = stmt.create_list(inp.orelse)


class If(stmt):
    test: expr
    body: List[stmt]
    orelse: List[stmt]

    def __init__(self, inp: ast.If):
        super().__init__(inp)
        self.test = expr.create(inp.test)
        self.body = stmt.create_list(inp.body)
        self.orelse = stmt.create_list(inp.orelse)


class With(stmt):
    items: List[withitem]
    body: List[stmt]
    
    def __init__(self, inp: ast.With):
        super().__init__(inp)
        self.items = [withitem(i) for i in inp.items]
        self.body = stmt.create_list(inp.body)


class AsyncWith(stmt):
    items: List[withitem]
    body: List[stmt]
    
    def __init__(self, inp: ast.AsyncWith):
        super().__init__(inp)
        self.items = [withitem(i) for i in inp.items]
        self.body = stmt.create_list(inp.body)


class Raise(stmt):
    exc: Optional[expr]
    cause: Optional[expr]
    
    def __init__(self, inp: ast.Raise):
        super().__init__(inp)
        self.exc = None if inp.exc is None else expr.create(inp.exc)
        self.cause = None if inp.cause is None else expr.create(inp.cause)


class Try(stmt):
    body: List[stmt]
    handlers: List[excepthandler]
    orelse: List[stmt]
    finalbody: List[stmt]
    
    def __init__(self, inp: ast.Try):
        super().__init__(inp)
        self.body = stmt.create_list(inp.body)
        self.orelse = stmt.create_list(inp.orelse)
        self.finalbody = stmt.create_list(inp.finalbody)


class Assert(stmt):
    test: expr
    msg: Optional[expr]
    
    def __init__(self, inp: ast.Assert):
        super().__init__(inp)
        self.test = expr.create(inp.test)
        self.msg = None if inp.msg is None else expr.create(inp.msg)


class Import(stmt):
    strs: List[_alias]

    def __init__(self, inp: ast.Import):
        super().__init__(inp)
        self.strs = [_alias(i) for i in inp.names]


class ImportFrom(stmt):
    module: Optional[str]
    strs: List[_alias]
    # level: Optional[init]

    def __init__(self, inp: ast.ImportFrom):
        super().__init__(inp)
        self.module = inp.module
        self.strs = [_alias(i) for i in inp.names]
        # self.level = inp.level
        # TODO: What is level?
        # 喵喵喵？


class Global(stmt):
    strs: List[str]
    
    def __init__(self, inp: ast.Global):
        # TODO: raise InvalidExprError
        super().__init__(inp)
        self.strs = inp.names


class Nonlocal(stmt):
    strs: List[str]
    
    def __init__(self, inp: ast.Nonlocal):
        # TODO: raise InvalidExprError
        super().__init__(inp)
        self.strs = inp.names


class Expr(stmt):
    value: expr

    def __init__(self, inp: ast.Expr):
        super().__init__(inp)
        self.value = expr.create(inp.value)


class ControlStatement(stmt, Enum):
    Pass = 'Pass'
    Break = 'Break'
    Continue = 'Continue'

    def __init__(self, inp: ast.operator):
        super().__init__(inp)
        # TODO: 
        ...



class expr(XAST):
    @staticmethod
    def create(inp: ast.expr) -> expr:
        ...

    @staticmethod
    def create_list(inp: List[ast.expr]) -> List[expr]:
        return [expr.create(i) for i in inp]


class BoolOp(expr):
    op: boolop
    values: List[expr]
    
    def __init__(self, inp: ast.BoolOp):
        super().__init__(inp)
        self.op = boolop(inp.op)
        self.values = expr.create_list(inp.values)
        
class BinOp(expr):
    left: expr
    right: expr
    op: operator

    def __init__(self, inp: ast.BinOp):
        super().__init__(inp)
        self.left = expr.create(inp.left)
        self.right = expr.create(inp.right)
        self.op = operator(inp.op)


class UnaryOp(expr):
    op: unaryop
    operand: expr

    def __init__(self, inp: ast.UnaryOp):
        super().__init__(inp)
        self.op = unaryop(inp.op)
        self.operand = expr.create(inp.operand)


class Lambda(expr):
    args: List[arg]
    body: expr

    def __init__(self, inp: ast.Lambda):
        super().__init__(inp)
        self.args = from_arguments_to_arg(inp.args)
        self.body = expr.create(inp.body)


class IfExp(expr):
    test: expr
    body: expr
    orelse: expr
    
    def __init__(self, inp: ast.IfExp):
        super().__init__(inp)
        self.test = expr.create(inp.test)
        self.body = expr.create(inp.test)
        self.orelse = expr.create(inp.orelse)


class Dict(expr):
    keys: List[Optional[expr]]
    values: List[expr]

    def __init__(self, inp: ast.Dict):
        super().__init__(inp)
        self.keys = [
            None if i is None else expr.create(i)
                for i in inp.keys] # WTF???
        self.values = expr.create_list(inp.values)
    

class Set(expr):
    elts: List[expr]

    def __init__(self, inp: ast.Set):
        super().__init__(inp)
        self.elts = expr.create_list(inp.elts)


class ListComp(expr):
    elt: expr
    generators: List[comprehension]
    
    def __init__(self, inp: ast.ListComp):
        super().__init__(inp)
        self.elts = expr.create(inp.elt)
        self.generators = [comprehension(i) for i in inp.generators]


class SetComp(expr):
    elt: expr
    generators: List[comprehension]
    
    def __init__(self, inp: ast.SetComp):
        super().__init__(inp)
        self.elts = expr.create(inp.elt)
        self.generators = [comprehension(i) for i in inp.generators]


class DictComp(expr):
    key: expr
    value: expr
    generators: List[comprehension]
    
    def __init__(self, inp: ast.DictComp):
        super().__init__(inp)
        self.key = expr.create(inp.key)
        self.value = expr.create(inp.value)
        self.generators = [comprehension(i) for i in inp.generators]


class GeneratorExp(expr):
    elt: expr
    generators: List[comprehension]
    
    def __init__(self, inp: ast.SetComp):
        super().__init__(inp)
        self.elts = expr.create(inp.elt)
        self.generators = [comprehension(i) for i in inp.generators]


class Await(expr):
    value: expr

    def __init__(self, inp: ast.Await):
        super().__init__(inp)
        self.value = expr.create(inp.value)


class Yield(expr):
    value: Optional[expr]

    def __init__(self, inp: ast.Yield):
        super().__init__(inp)
        self.value = None if inp.value is None else expr.create(inp.value)


class YieldFrom(expr):
    value: expr

    def __init__(self, inp: ast.YieldFrom):
        super().__init__(inp)
        self.value = expr.create(inp.value)


class Compare(expr):
    left: expr
    ops: List[cmpop]
    comparators: List[expr]

    def __init__(self, inp: ast.Compare):
        super().__init__(inp)
        self.left = expr.create(inp.left)
        self.ops = [cmpop(i) for i in inp.ops]
        self.comparators = expr.create_list(inp.comparators)


class Call(expr):
    func: expr
    args: List[expr]

    def __init__(self, inp: ast.Call):
        assert len(inp.keywords) == 0
        super().__init__(inp)
        self.func = expr.create(inp.func)
        self.args = expr.create_list(inp.args)


class Num(expr):
    value: object

    def __init__(self, inp: ast.Num):
        super().__init__(inp)
        self.value = inp.n


class Str(expr):
    value: str
    def __init__(self, inp: ast.Str):
        super().__init__(inp)
        self.value = inp.s


class Byte(expr):
    value: bytes
    
    def __init__(self, inp: ast.Bytes):
        super().__init__(inp)
        self.value = inp.s


class JoinedStr(expr):
    value: List[expr]
    
    def __init__(self, inp: ast.JoinedStr):
        super().__init__(inp)
        self.value = expr.create_list(inp.values)


class FormattedValue(expr):
    value: expr
    conversion: Optional[int]
    format_spec: Optional[expr]
    
    def __init__(self, inp: ast.FormattedValue):
        super().__init__(inp)
        self.value = expr.create(inp.value)
        self.conversion = inp.conversion
        self.format_spec = None if inp.format_spec is None else expr.create(inp.format_spec)


class NameConstant(expr):
    value: Any
    
    def __init__(self, inp: ast.NameConstant):
        super().__init__(inp)
        self.value = inp.value


class Ellipsis(expr):
    def __init__(self, inp: ast.Ellipsis):
        super().__init__(inp)


class Constant(expr):
    value: Any
    
    def __init__(self, inp: ast.Constant):
        super().__init__(inp)
        self.value = inp.value


class Attribute(expr):
    value: expr
    attr: str
    # ctx: expr_context

    def __init__(self, inp: ast.Attribute):
        super().__init__(inp)
        self.value = expr.create(inp.value)
        self.attr = inp.attr
        # self.ctx = expr_context(inp.ctx)



class Subscript(expr):
    value: expr
    slice: slice
    # ctx: expr_context
    
    def __init__(self, inp: ast.Subscript):
        super().__init__(inp)
        self.value = expr.create(inp.value)
        self.slice = slice(inp.slice)
        # self.ctx = expr_context(inp.ctx)


class Starred(expr):
    value: expr
    # ctx: expr_context

    def __init__(self, inp: ast.Starred):
        super().__init__(inp)
        self.value = expr.create(inp.value)
        # self.ctx = expr_context(inp.ctx)


class Name(expr):
    id: str
    # ctx: expr_context

    def __init__(self, inp: ast.Name):
        super().__init__(inp)
        self.id = inp.id
        # self.ctx = expr_context(inp.ctx)


class _List(expr):
    elts: List[expr]
    # ctx: expr_context

    def __init__(self, inp: ast.List):
        super().__init__(inp)
        self.elts = expr.create_list(inp.elts)
        # self.ctx = expr_context(inp.ctx)

class Tuple(expr):
    elts: List[expr]
    # ctx: expr_context

    def __init__(self, inp: ast.Tuple):
        super().__init__(inp)
        self.elts = expr.create_list(inp.elts)
        # self.ctx = expr_context(inp.ctx)


class expr_context(XAST):
    Load = 'Load'
    Store = 'Store'
    Del = 'Del'
    AugLoad = 'AugLoad'
    AugStore = 'AugStore'
    Param = 'Param'

    def __init__(self, inp: ast.expr_context):
        super().__init__(inp)        

class boolop(XAST, Enum):
    And = 'And'
    Or = 'Or'

    value: boolop

    def __init__(self, inp: ast.boolop):
        super().__init__(inp)
        self.value = {
            ast.And: boolop.And,
            ast.Or: boolop.Or,
        }[type(inp)]


      
class operator(XAST, Enum):
    Add = 'Add'
    Sub = 'Sub'
    Mult = 'Mult'
    MatMult = 'MatMult'
    Div = 'Div'
    Mod = 'Mod'
    Pow = 'Pow'
    LShift = 'LShift'
    RShift = 'RShift'
    BitOr = 'BitOr'
    BitXor = 'BitXor'
    BitAnd = 'BitAnd'
    FloorDiv = 'FloorDiv'

    value: operator

    def __init__(self, inp: ast.operator):
        super().__init__(inp)
        # TODO: 
        ...

class unaryop(XAST, Enum):
    Invert = 'Invert'
    Not = 'Not'
    UAdd = 'UAdd'
    USub = 'USub'

    value: unaryop

    def __init__(self, inp: ast.unaryop):
        super().__init__(inp)
        self.value = {
            ast.Invert: unaryop.Invert,
            ast.Not: unaryop.Not,
            ast.UAdd: unaryop.UAdd,
            ast.USub: unaryop.USub,
        }[type(inp)]


class cmpop(XAST, Enum):
    Eq  = 'Eq'
    NotEq = 'NotEq'
    Lt = 'Lt'
    LtE = 'LtE'
    Gt   = 'Gt  '
    GtE = 'GtE'
    Is = 'Is'
    IsNot = 'IsNot'
    In = 'In'
    NotIn = 'NotIn'

    value: str

    def __init__(self, inp: ast.cmpop):
        super().__init__(inp)
        ...


class comprehension(XAST):
    target: expr
    iter: expr
    ifs: List[expr]
    is_async: int

    def __init__(self, inp: ast.comprehension):
        super().__init__(inp)
        self.target = expr.create(inp.target)
        self.iter = expr.create(inp.iter)
        self.ifs = expr.create_list(inp.ifs)
        self.is_async = inp.is_async


class excepthandler(XAST):
    typ: Optional[expr]
    str: Optional[str]
    body: List[stmt]

    def __init__(self, inp: ast.ExceptHandler):
        super().__init__(inp)
        self.typ = None if inp.type is None else expr.create(inp.type)
        self.str = inp.name
        self.body = stmt.create_list(inp.body)


class arg(XAST):
    str: str
    annotation: Optional[expr]

    def __init__(self, inp: ast.arg):
        super().__init__(inp)
        self.str = inp.arg
        self.annotation = None
        if inp.annotation:
            self.annotation = expr.create(inp.annotation)


class _alias(XAST):
    name: str
    asname: Optional[str]

    def __init__(self, inp: ast.alias):
        super().__init__(inp)
        self.name = inp.name
        self.asstr = inp.asname


class withitem(XAST):
    context_expr: expr
    vars: Optional[expr]
    
    def __init__(self, inp: ast.withitem):
        super().__init__(inp)
        self.context_expr = expr.create(inp.context_expr)
        self.vars = None if inp.optional_vars is None else expr.create(inp.optional_vars)
        