from _ast import AST
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional

from typing_extensions import TypedDict

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


class ClassInfo(TypedDict):
    name: Name
    fullname: Name
    items: Dict[Name, TypeInfo]
    methods: Dict[Name, FunctionInfo]
    static_items: Dict[Name, Union[TypeInfo, AST]]
    static_function: Dict[Name, FunctionInfo]
    parent: List['ClassInfo']


class FileMataInfo(TypedDict):
    name: Name
    fullname: Name
    path: Path
    import_list: Dict[Name, Union[ClassInfo, FunctionInfo, Name, 'FileMataInfo']]
    classes: Dict[Name, ClassInfo]
    functions: Dict[Name, FunctionInfo]
    do_block: List[ExprInfo]
    export_list: List[Name]
