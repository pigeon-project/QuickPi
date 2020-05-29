from ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional

from typing_extensions import ClassVar

from .type_info import TypeInfo, ProperType, QTypeVar
from .utils import Name


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
            is_async: bool,
            name: Name,
            fullname: Name,
            body: List[AST],
            parent: 'FunctionInfo',
            top_level: 'ModuleMataInfo',
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
