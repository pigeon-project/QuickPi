from typing import TypeVar, List, Dict, Set, Optional

from typing_extensions import ClassVar

from .mata_info import Context, ClassInfo, OneNameSpace
from .utils import Name

type_id_alloc: int = 0


def alloc_type_id() -> int:
    global type_id_alloc
    res = type_id_alloc
    type_id_alloc += 1
    return res


class TypeInfo:
    def __init__(self):
        ...

    def __str__(self):
        ...

    def join(self, other: 'TypeInfo') -> 'TypeInfo':
        ...

    def isinstense(self, other: 'TypeInfo') -> bool:
        ...


class TypeRef(TypeInfo):
    name: TypeVar[Name]
    # fullname: TypeVar[Optional[Name]]
    context: TypeVar[Optional[OneNameSpace]]

    def __init__(
            self,
            name: Name,
            # fullname: Optional[Name] = None,
            context: Optional[OneNameSpace] = None):
        super().__init__()
        self.name = name
        # self.fullname = fullname
        self.context = context

    def bind_context(self, context: OneNameSpace):
        self.context = context

    def get_true_type(self, context: Optional[OneNameSpace] = None) -> ClassInfo:
        if self.context:
            return self.context.find_name(self.name)
        if context:
            return context.find_name(self.name)
        raise RuntimeError('没有绑定context还不传context？给爷爪巴')

    def isinstense(self, other: 'TypeInfo', context: Optional[OneNameSpace] = None) -> bool:
        return self.get_true_type().isinstense(other)


class QTypeVar(TypeInfo):
    pass


class TypeId(QTypeVar):
    id: ClassVar[int]

    def __init__(self):
        super().__init__()
        self.id = alloc_type_id()


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

# builtin_object = TypeRef('bool', 'qpy.builtin.object')
# builtin_none = TypeRef('none', 'qpy.builtin.none')
# builtin_bool = TypeRef('bool', 'qpy.builtin.bool')
# builtin_str = TypeRef('str', 'qpy.builtin.str')
# builtin_int = TypeRef('int', 'qpy.builtin.int')
# builtin_float = TypeRef('float', 'qpy.builtin.float')
# builtin_bytes = TypeRef('bytes', 'qpy.builtin.bytes')
