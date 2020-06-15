from typing import List, Optional
from enum import Enum
import ast

import mata_info as mi
from mata_info import NameSpace
from bytecode import ByteCode
from utils import trait, PosInfo


@trait
class XAST:
    pos: PosInfo

    def __init__(self, inp: ast.AST):
        self.pos = PosInfo(inp.lineno, inp.col_offset)
    def type_check(self, ctx: NameSpace): ...
    # def codegen(self, ctx: NameSpace) -> ByteCode: ...


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
    name: str
    args: List[arg]
    body: List[stmt]
    decorator_list: List[expr]
    returns: Optional[expr]
    

    def __init__(self, inp: ast.FunctionDef):
        super().__init__(inp)
        self.name = inp.name
        self.args = [arg(i) for i in inp.args.args]
        self.body = stmt.create_list(inp.body)
        self.decorator_list = expr.create_list(inp.decorator_list)
        self.returns = None if inp.returns is None else expr.create(inp.returns)


class AsyncFunctionDef(stmt):
    name: str
    args: List[arg]
    body: List[stmt]
    decorator_list: List[expr]
    returns: Optional[expr]

    def __init__(self, inp: ast.AsyncFunctionDef):
        super().__init__(inp)
        self.name = inp.name
        args = inp.args
        assert not args.vararg
        assert not args.kwonlyargs
        assert not args.kw_defaults
        assert not args.kwarg
        assert not args.defaults
        self.args = [arg(i) for i in args.args]
        self.body = stmt.create_list(inp.body)
        self.decorator_list = expr.create_list(inp.decorator_list)
        self.returns = None if inp.returns is None else expr.create(inp.returns)


class ClassDef(stmt):
    name: str
    bases: List[expr]
    body: List[stmt]
    decorator_list: List[expr]

    def __init__(self, inp: ast.ClassDef):
        super().__init__(inp)
        self.name = inp.name
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
        self.target = expr.create(inp.target)
        self.value = expr.create(inp.value)
        self.op = operator(inp.op)


class AnnAssign(stmt):
    target: expr
    annotation: expr
    value: Optional[expr]

    def __init__(self, inp: ast.AnnAssign):
        self.target = expr.create(inp.target)
        self.annotation = expr.create(inp.annotation)
        self.value = None if inp.value is None else expr.create(inp.value)


class expr(XAST):
    @staticmethod
    def create(inp: ast.expr) -> expr:
        ...

    @staticmethod
    def create_list(inp: List[ast.expr]) -> List[expr]:
        return [expr.create(i) for i in inp]


class arg(XAST):
    name: str
    annotation: Optional[expr]

    def __init__(self, inp: ast.arg):
        super().__init__(inp)
        self.name = inp.arg
        self.annotation = None
        if inp.annotation:
            self.annotation = expr.create(inp.annotation)

        
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

    def __init__(self, inp: ast.operator):
        # TODO: 
        ...