from _ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional

from typing_extensions import TypedDict, ClassVar

from .type_info import TypeInfo
from .utils import Name


class ExprInfo(TypedDict):
    expr: AST
    type: TypeInfo


class FunctionInfo(TypedDict):
    is_loose: bool
    is_async: bool
    is_pure: bool
    name: Name
    fullname: Name
    params: Dict[Name, Tuple[Optional[TypeInfo], Optional[AST]]]
    variables: List[Union[Name, TypeInfo]]
    body: List[AST]
    parent: Tuple['FunctionInfo']
    # top_level: 'FileMataInfo'


class ClassInfo:
    name: ClassVar[Name]
    fullname: ClassVar[Name]
    items: ClassVar[Dict[Name, TypeInfo]]
    methods: ClassVar[Dict[Name, FunctionInfo]]
    static_items: ClassVar[Dict[Name, Tuple[TypeInfo, AST]]]
    static_function: ClassVar[Dict[Name, FunctionInfo]]
    parent: ClassVar[List['ClassInfo']]
    top_level: ClassVar['FileMataInfo']

    def __init__(
            self,
            name: Name,
            fullname: Name,
            parent: List['ClassInfo'],
            top_level: 'FileMataInfo'):
        self.name = name
        self.fullname = fullname
        self.items = {}
        self.methods = {}
        self.static_items = {}
        self.static_function = {}
        self.parent = parent
        self.top_level = top_level

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


class FileMataInfo(TypedDict):
    name: Name
    fullname: Name
    path: Path
    import_list: Dict[Name, Union[ClassInfo, FunctionInfo, Name, 'FileMataInfo']]
    classes: Dict[Name, ClassInfo]
    functions: Dict[Name, FunctionInfo]
    do_block: List[ExprInfo]
    export_list: List[Name]


Context = Union[FileMataInfo, ClassInfo, FunctionInfo]
