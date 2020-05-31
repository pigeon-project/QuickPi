from ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Set

from typing_extensions import ClassVar

from .utils import Name, alloc_type_id, PosInfo


class TypeInfo:
    type_id: ClassVar[int]
    pos: ClassVar[Optional[PosInfo]]
    top_level: ClassVar['ModuleMataInfo']

    def __init__(self, top_level: 'ModuleMataInfo', pos: Optional[PosInfo] = None):
        self.type_id = alloc_type_id()
        self.top_level = top_level
        self.pos = pos

    def __str__(self):
        ...

    # def join(self, other: 'TypeInfo') -> 'TypeInfo':
    #     ...

    # def isinstense(self, other: 'TypeInfo') -> bool:
    #     ...


class QTypeVar(TypeInfo):
    trait_constraint: ClassVar[Set['TraitInfo']]


class ProperType(TypeInfo):
    # def join(self, other: 'TypeInfo') -> 'TypeInfo':
    #     if isinstance(self, AnyType) or isinstance(other, AnyType):
    #         return AnyType()
    #     return UnionType({self, other})
    pass


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


class CallableType(ProperType):
    type_arrow: ClassVar[List[TypeInfo]]
    throws: ClassVar[List[TypeInfo]]

    def __init__(
            self,
            pos: PosInfo,
            type_arrow: List[TypeInfo],
            throws: List[TypeInfo],
            top_level: 'ModuleMataInfo'
    ):
        super().__init__(top_level, pos)
        self.type_arrow = type_arrow
        self.throws = throws


class FunctionInfo(OneNameSpace, ProperType):
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
            pos: PosInfo,
            body: List[AST],
            parent: 'FunctionInfo',
            top_level: 'ModuleMataInfo',
            is_async: bool = False,
            strict: bool = True,
    ):
        super().__init__(top_level, pos)
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
        # if self.throw is None:
        #     self.throw = typeinfo
        # else:
        #     self.throw.join(typeinfo)
        pass

    def get_top_level(self) -> 'ModuleMataInfo':
        return self.top_level


'''demo
@forall(a)
def id(a: a): a

@entry_point
def main(_):
    a = id(1)
    print(a)
    0
'''

'''

@trait
@forall(T)
class Add:
    def __add__(self, other: T) -> T: ...

def double(i): i + i

# double :: (T | Add) -> (T | Add)

@trait
@forall(T)  
class Enter:
    def __enter__(self) -> T: ...

@trait
class Exit:
    def __exit__(self) -> Unit: ...

@trait
class IDisposable(T): Enter[T] + Exit

...
with foo() as obj:
    # obj :: (a | IDisposable[T])
    ...
...
'''


class TraitInfo(ProperType):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    type_vars: ClassVar[List[QTypeVar]]
    methods: ClassVar[List[CallableType]]

    def __init__(
            self,
            pos: PosInfo,
            name: Name,
            fullname: Name,
            type_vars: List[QTypeVar],
            methods: List[CallableType],
            top_level: 'ModuleMataInfo'
    ):
        super().__init__(top_level, pos)
        self.name = name
        self.fullname = fullname
        self.type_vars = type_vars
        self.methods = methods

    def __str__(self):
        return self.fullname


class ImplInfo:
    methods: ClassVar[List[FunctionInfo]]


class ClassInfo(TwoNameSpace, ProperType):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    type_vars: ClassVar[Dict[Name, QTypeVar]]
    items: ClassVar[Dict[Name, TypeInfo]]
    methods: ClassVar[Dict[Name, FunctionInfo]]
    traits: ClassVar[Dict[Name, Union['TypeRef', 'TypeApply']]]
    impls: ClassVar[Dict[Name, ImplInfo]]
    impl: ClassVar[ImplInfo]
    top_level: ClassVar['ModuleMataInfo']

    def __init__(
            self,
            name: Name,
            fullname: Name,
            pos: PosInfo,
            traits: Dict[Name, TraitInfo],
            top_level: 'ModuleMataInfo'
    ):
        super().__init__(top_level, pos)
        self.name = name
        self.fullname = fullname
        self.type_vars = {}
        self.items = {}
        self.methods = {}
        self.traits = traits
        self.impls = {}

    def get_top_level(self) -> 'ModuleMataInfo':
        return self.top_level

    def find_item(self, name: Name) -> TypeInfo:
        r: Optional[TypeInfo] = self.items.get(name)
        if r:
            return r
        raise KeyError

    '''
    def find_method(self, name: Name) -> FunctionInfo:
        r: Optional[FunctionInfo] = self.methods.get(name)
        if r is None:
            for i in self.parent:
                r = i.find_method(name)
                if r is not None:
                    return r
        raise KeyError
    '''


class ModuleMataInfo(OneNameSpace):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    path: ClassVar[Path]
    import_list: ClassVar[Dict[Name, 'Context']]
    bind: ClassVar[Dict[Name, 'Context']]
    # do_block: ClassVar[List[AST]]
    # export_list: ClassVar[List[Name]]

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
        # self.do_block = []
        # self.export_list = []

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


Context = Union[ModuleMataInfo, FunctionInfo, ClassInfo, TraitInfo, ObjectBind]


class TypeRef(TypeInfo):
    name: ClassVar[Name]
    # fullname: TypeVar[Optional[Name]]
    context: ClassVar[Optional[Dict[Name, TypeInfo]]]

    def __init__(
            self,
            name: Name,
            # fullname: Optional[Name] = None,
            top_level: 'ModuleMataInfo',
            pos: Optional[PosInfo] = None,
            context: Optional[OneNameSpace] = None):
        super().__init__(top_level, pos)
        self.name = name
        # self.fullname = fullname
        self.context = context

    def bind_context(self, context: Dict[Name, TypeInfo]):
        self.context = context

    def get_true_type(self, context: Optional[Dict[Name, TypeInfo]] = None) -> TypeInfo:
        if self.context:
            return self.context[self.name]
        if context:
            return context[self.name]
        raise RuntimeError('没有绑定context还不传context？给爷爪巴')

    # def isinstense(self, other: 'TypeInfo', context: Optional[OneNameSpace] = None) -> bool:
    #     return self.get_true_type().isinstense(other)


class TypeId(QTypeVar):
    id: ClassVar[int]

    def __init__(self, top_level: 'ModuleMataInfo', pos: Optional[PosInfo] = None):
        super().__init__(top_level, pos)
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
    typen: ClassVar[TypeRef]
    type_prarms: ClassVar[List[TypeInfo]]

    def __init__(
            self,
            top_level: 'ModuleMataInfo',
            pos: PosInfo,
            typen: TypeRef,
            type_prarms: List[TypeInfo]
    ):
        super().__init__(top_level, pos)
        self.typen = typen
        self.type_prarms = type_prarms


# class TypedDictType(ProperType):
#     record: ClassVar[Dict[Name, TypeInfo]]


# class UnionType(ProperType):
#     include_type: ClassVar[Set[TypeInfo]]
#
#     def __init__(self, i: Set[TypeInfo]):
#         super().__init__()
#         self.include_type = i
#
#     def join(self, other: 'TypeInfo') -> 'TypeInfo':
#         if isinstance(other, AnyType):
#             return AnyType()
#         self.include_type.add(other)
#         return self


class TupleType(ProperType):
    include_type: ClassVar[List[TypeInfo]]


class ListType(ProperType):
    include_type: ClassVar[TypeInfo]


builtin_type = ('object', 'bool', 'int', 'float', 'str', 'tuple', 'list', 'set', 'dict')

builtin_module = ModuleMataInfo('builtins', 'quickpi.builtins', 'core/builtins.qpi')

builtin_object = TypeRef('bool', builtin_module)
builtin_none = TypeRef('none', builtin_module)
builtin_bool = TypeRef('bool', builtin_module)
builtin_str = TypeRef('str', builtin_module)
builtin_int = TypeRef('int', builtin_module)
builtin_float = TypeRef('float', builtin_module)
builtin_bytes = TypeRef('bytes', builtin_module)
