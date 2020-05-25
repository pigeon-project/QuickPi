from ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Any

from typing_extensions import TypedDict, ClassVar

from .type_info import TypeInfo
from .utils import Name


class NameSpace:
    def get_top_level(self) -> 'NameSpace':
        pass


class OneNameSpace(NameSpace):
    def find_name(self, name: Name) -> Any:
        ...


class TwoNameSpace(NameSpace):
    pass


class ObjectBind:
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    typeinfo: ClassVar[Optional[TypeInfo]]
    top_level: ClassVar['ModuleMataInfo']

    # value: ClassVar[Optional[AST]]
    def __init__(
            self,
            name: Name,
            fullname: Name,
            typeinfo: Optional[TypeInfo] = None
    ):
        self.name = name
        self.fullname = fullname
        self.typeinfo = typeinfo


class FunctionInfo(OneNameSpace):
    strict: bool
    is_async: bool
    is_pure: Optional[bool]
    name: Name
    fullname: Name
    params: Dict[Name, Tuple[Optional[TypeInfo], Optional[AST]]]
    variables: List[Union[Name, TypeInfo]]
    body: List[AST]
    parent: Tuple['FunctionInfo']
    top_level: ClassVar['ModuleMataInfo']

    def get_top_level(self) -> 'ModuleMataInfo':
        return self.top_level


class ClassInfo(TwoNameSpace):
    name: ClassVar[Name]
    fullname: ClassVar[Name]
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
            top_level: 'ModuleMataInfo'):
        self.name = name
        self.fullname = fullname
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

    def find_name(self, name: Name) -> Optional['Context']:
        r = self.bind.get(name)
        if r is None:
            r = self.import_list.get(name)
        return r

    def get_top_level(self) -> 'ModuleMataInfo':
        return self


Context = Union[ModuleMataInfo, FunctionInfo, ClassInfo, ObjectBind]
