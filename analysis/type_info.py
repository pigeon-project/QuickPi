from typing import TypeVar, List, Dict

from typing_extensions import ClassVar

from .utils import Name

builtin_type = ('object', 'bool', 'int', 'float', 'str', 'tuple', 'list', 'set', 'dict')


class TypeInfo:
    def __init__(self):
        pass


class TypeRef(TypeInfo):
    name: TypeVar[Name]

    def __init__(self, name: Name):
        super().__init__()
        self.name = name


"""
class AliasType(TypeInfo):
    pass
"""


class ProperType(TypeInfo):
    pass


class AnyType(ProperType):
    pass


class BottomType(ProperType):
    pass


class NoMemberType(ProperType):
    pass


class NoneType(NoMemberType):
    pass


class TypeApply(ProperType):
    pass


class TypedDictType(ProperType):
    record: ClassVar[Dict[Name, TypeInfo]]


class UnionType(ProperType):
    include_type: ClassVar[List[TypeInfo]]


class TupleType(ProperType):
    include_type: ClassVar[List[TypeInfo]]


class ListType(ProperType):
    include_type: ClassVar[TypeInfo]
