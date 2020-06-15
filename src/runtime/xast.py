import ast

from .mata_info import NameSpace
from .utils import trait

@trait
class ByteCode:
    ...

@trait
class XAST:
    def __init__(self, i: ast.AST): ...
    def type_check(self, ctx: NameSpace): ...
    def codegen(self, ctx: NameSpace) -> ByteCode: ...