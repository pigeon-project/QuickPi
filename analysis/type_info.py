from typing import TypeVar, List, Dict, Set, Optional

from typing_extensions import ClassVar

from .mata_info import Context, ClassInfo
from .utils import Name


class TypeInfo:
    def __init__(self):
        ...

    def __str__(self):
        ...

    # def join(self, other: 'TypeInfo') -> 'TypeInfo':
    #     ...


class TypeRef(TypeInfo):
    name: TypeVar[Name]
    fullname: TypeVar[Optional[Name]]

    def __init__(self, name: Name, fullname: Optional[Name] = None):
        super().__init__()
        self.name = name
        self.fullname = fullname

    def get_true_type(self, context: Context) -> ClassInfo:
        pass


"""
class AliasType(TypeInfo):
    pass
"""


class ProperType(TypeInfo):
    def join(self, other: 'TypeInfo') -> 'TypeInfo':
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return AnyType()
        return UnionType({self, other})


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
    include_type: ClassVar[Set[TypeInfo]]

    def __init__(self, i: Set[TypeInfo]):
        super().__init__()
        self.include_type = i


class TupleType(ProperType):
    include_type: ClassVar[List[TypeInfo]]


class ListType(ProperType):
    include_type: ClassVar[TypeInfo]


builtin_type = ('object', 'bool', 'int', 'float', 'str', 'tuple', 'list', 'set', 'dict')

builtin_object = TypeRef('bool', 'qpy.builtin.object')
builtin_none = TypeRef('none', 'qpy.builtin.none')
builtin_bool = TypeRef('bool', 'qpy.builtin.bool')
builtin_str = TypeRef('str', 'qpy.builtin.str')
builtin_int = TypeRef('int', 'qpy.builtin.int')
builtin_float = TypeRef('float', 'qpy.builtin.float')
builtin_bytes = TypeRef('bytes', 'qpy.builtin.bytes')
