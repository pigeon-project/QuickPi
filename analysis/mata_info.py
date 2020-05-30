from ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Set

from typing_extensions import ClassVar

from .utils import Name, alloc_type_id


class TypeInfo:
    def __init__(self):
        ...

    def __str__(self):
        ...

    def join(self, other: 'TypeInfo') -> 'TypeInfo':
        ...

    def isinstense(self, other: 'TypeInfo') -> bool:
        ...


class QTypeVar(TypeInfo):
    pass


class ProperType(TypeInfo):
    def join(self, other: 'TypeInfo') -> 'TypeInfo':
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return AnyType()
        return UnionType({self, other})


class NameSpace:
    def get_top_level(self) -> 'NameSpace':
        pass


class OneNameSpace(NameSpace):
    def add_symbol(self, name: Name, value: 'Context'):
        ...

    def find_name(self, name: Name) -> 'Context':
        ...


class TwoNameSpace(NameSpace):
    pass


class ObjectBind:
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    typeinfo: ClassVar[TypeInfo]
    top_level: ClassVar['ModuleMataInfo']

    # value: ClassVar[Optional[AST]]
    def __init__(
            self,
            name: Name,
            fullname: Name,
            typeinfo: TypeInfo
    ):
        self.name = name
        self.fullname = fullname
        self.typeinfo = typeinfo

    # class Callable(ProperType):
    #     params_type: ClassVar[UnionType[]]
    # pass


class FunctionInfo(OneNameSpace, ProperType):
    strict: ClassVar[bool]
    is_async: ClassVar[bool]
    is_pure: ClassVar[Optional[bool]]
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    type_vars: ClassVar[Dict[Name, QTypeVar]]
    params: ClassVar[Dict[Name, Tuple[TypeInfo, Optional[AST]]]]
    throw: ClassVar[Optional[TypeInfo]]
    variables: ClassVar[Dict[Name, TypeInfo]]
    body: ClassVar[List[AST]]
    parent: ClassVar[Optional['FunctionInfo']]
    top_level: ClassVar['ModuleMataInfo']

    def __init__(
            self,
            name: Name,
            fullname: Name,
            body: List[AST],
            parent: 'FunctionInfo',
            top_level: 'ModuleMataInfo',
            is_async: bool = False,
            strict: bool = True,
    ):
        super().__init__()
        self.strict = strict
        self.is_async = is_async
        self.name = name
        self.fullname = fullname
        self.is_pure = None
        self.type_vars = {}
        self.params = {}
        self.throw = None
        self.variables = {}
        self.body = body
        self.parent = parent
        self.top_level = top_level

    def add_symbol(self, name: Name, value: 'Context'):
        self.variables[name] = value

    def find_item(self, name: Name) -> TypeInfo:
        r: Optional[TypeInfo] = self.params.get(name)
        if r:
            return r
        r: Optional[TypeInfo] = self.variables.get(name)
        if r:
            return r
        if self.parent:
            r = self.parent.find_item(name)
            if r:
                return r
        # r: Optional[TypeInfo] = self.get_top_level().find_name(name)
        # if r:
        #     return r
        raise KeyError

    def add_throw_type(self, typeinfo: TypeInfo):
        if self.throw is None:
            self.throw = typeinfo
        else:
            self.throw.join(typeinfo)

    def get_top_level(self) -> 'ModuleMataInfo':
        return self.top_level


class ClassInfo(TwoNameSpace, ProperType):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    type_vars: ClassVar[Dict[Name, QTypeVar]]
    items: ClassVar[Dict[Name, TypeInfo]]
    methods: ClassVar[Dict[Name, FunctionInfo]]
    static_items: ClassVar[Dict[Name, Tuple[TypeInfo, AST]]]
    static_function: ClassVar[Dict[Name, FunctionInfo]]
    parent: ClassVar[List['ClassInfo']]
    top_level: ClassVar['ModuleMataInfo']

    def __init__(
            self,
            name: Name,
            fullname: Name,
            parent: List['ClassInfo'],
            top_level: 'ModuleMataInfo'
    ):
        super().__init__()
        self.name = name
        self.fullname = fullname
        self.type_vars = {}
        self.items = {}
        self.methods = {}
        self.static_items = {}
        self.static_function = {}
        self.parent = parent
        self.top_level = top_level

    def get_top_level(self) -> 'ModuleMataInfo':
        return self.top_level

    def is_instance(self, other: 'ClassInfo') -> bool:
        if self is other:
            return True
        for i in self.parent:
            if i.is_instance(other):
                return True
        return False

    def find_item(self, name: Name) -> TypeInfo:
        r: Optional[TypeInfo] = self.items.get(name)
        if r:
            return r
        for i in self.parent:
            r = i.find_item(name)
            if r is not None:
                return r
        raise KeyError

    def find_static_item(self, name: Name) -> Tuple[TypeInfo, AST]:
        r: Optional[Tuple[TypeInfo, AST]] = self.static_items.get(name)
        if r:
            return r
        for i in self.parent:
            r = i.find_static_item(name)
            if r is not None:
                return r
        raise KeyError

    def find_method(self, name: Name) -> FunctionInfo:
        r: Optional[FunctionInfo] = self.methods.get(name)
        if r is None:
            for i in self.parent:
                r = i.find_method(name)
                if r is not None:
                    return r
        raise KeyError

    def find_static_method(self, name: Name) -> FunctionInfo:
        r: Optional[FunctionInfo] = self.static_function.get(name)
        if r is None:
            for i in self.parent:
                r = i.find_static_method(name)
                if r is not None:
                    return r
        raise KeyError


class ModuleMataInfo(OneNameSpace):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    path: ClassVar[Path]
    import_list: ClassVar[Dict[Name, 'Context']]
    bind: ClassVar[Dict[Name, 'Context']]
    do_block: ClassVar[List[AST]]
    export_list: ClassVar[List[Name]]

    def __init__(
            self,
            name: ClassVar[Name],
            fullname: ClassVar[Name],
            path: ClassVar[Path]
    ):
        self.name = name
        self.fullname = fullname
        self.path = path
        self.import_list = {}
        self.bind = {}
        self.do_block = []
        self.export_list = []

    def add_symbol(self, name: Name, value: 'Context'):
        self.bind[name] = value

    def find_name(self, name: Name) -> Optional['Context']:
        r = self.bind.get(name)
        if r is None:
            r = self.import_list.get(name)
        return r

    def get_prev_name(self) -> str:
        return f'{self.fullname}.'

    def get_top_level(self) -> 'ModuleMataInfo':
        return self


Context = Union[ModuleMataInfo, FunctionInfo, ClassInfo, ObjectBind]


class TypeRef(TypeInfo):
    name: ClassVar[Name]
    # fullname: TypeVar[Optional[Name]]
    context: ClassVar[Optional[OneNameSpace]]

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


class TypeId(QTypeVar):
    id: ClassVar[int]

    def __init__(self):
        super().__init__()
        self.id = alloc_type_id()


"""
class AliasType(TypeInfo):
    pass
"""


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

    def join(self, other: 'TypeInfo') -> 'TypeInfo':
        if isinstance(other, AnyType):
            return AnyType()
        self.include_type.add(other)
        return self


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
