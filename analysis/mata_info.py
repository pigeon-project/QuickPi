from typing import List, Set, Iterable, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from functools import reduce
from ast import AST, stmt
from pathlib import Path

from .utils import trait, Name, intersection, PosInfo, AnalysisError, alloc_type_id


@trait
class TypeInfo:
    tid: int
    is_assign: bool

    def __new__(cls) -> TypeInfo:
        instance = object.__new__(cls)
        instance.tid = alloc_type_id()
        # instance.is_assign = True
        return instance

    def join(self, other: TypeInfo) -> UnionType:
        return UnionType({self, other})
    def get_true_type(self) -> TypeInfo:
        return self

    def get_traits(self) -> Set[TraitInfo]: ...

@trait
class TraitInfo(TypeInfo):
    def get_traits(self) -> Set[TraitInfo]:
        return {self}


@dataclass
class UnionType(TypeInfo):
    value: Set[TypeInfo]

    def join(self, other: TypeInfo) -> UnionType:
        if isinstance(other, UnionType):
            o: Set[TypeInfo] = other.value
        o = {other}
        return UnionType(self.value | o)

    def get_traits(self) -> Set[TraitInfo]:
        if len(self.value) == 0: return set()
        traits_list = [i.get_traits() for i in self.value]
        return set(reduce(intersection, traits_list))

class TypeVar(TypeInfo):
    name: Optional[Name]
    constraint: Optional[TypeInfo]

    def __init__(self, is_assign, name: Optional[Name]=None) -> None:
        self.is_assign = is_assign
        self.name = name
        self.constraint = None

    def add_constraint(self, t: TypeInfo) -> None:
        if self.constraint:
            self.constraint.join(t)
        else:
            self.constraint = t


@dataclass
class TypeRef(TypeInfo):
    name: Name
    ctx: Optional[NameSpace]

    def __init__(self, name: Name, ctx: Optional[NameSpace]=None) -> None:
        self.name = name
        self.ctx = ctx

    def bind_ctx(self, ctx: NameSpace) -> None:
        if not self.ctx:
            self.ctx = ctx
        assert False



@trait
class NameSpace:
    def get_top_level(self) -> Module: ...
    def find_name(self, name: Name) -> Optional[Union[NameSpace, TypeInfo]]: ...
    def register_name(self, name: Name, value: NameSpace): ...


@dataclass
class Module(NameSpace):
    name: Name
    fullname: Name
    path: Path
    import_list: Dict[Name, NameSpace]
    bind: Dict[Name, Union[NameSpace, TypeInfo]]

    def get_top_level(self) -> Module:
        return self

    def find_name(self, name: Name) -> Optional[Union[NameSpace, TypeInfo]]:
        r = self.bind.get(name)
        if r: return r
        return self.import_list.get(name)
    
    def register_name(self, name: Name, value: NameSpace) -> None:
        self.bind[name] = value


@dataclass
class Positional:
    pos: PosInfo


@dataclass
class Function(NameSpace, Positional):
    name: Name
    fullname: Name
    is_async: bool
    is_pure: Optional[bool]
    # type_vars: Dict[Name, TypeVar]
    type_vars: List[TypeVar]
    params: Dict[Name, TypeInfo] # (name: type = construct_expr, ...)
    return_type: Optional[TypeInfo]
    throw: Optional[TypeInfo]
    sub_namespace: Optional[NameSpace]
    body: List[stmt]
    parent: NameSpace
    top_level: Module

    def get_top_level(self) -> Module:
        return self.top_level

    def find_name(self, name: Name) -> Optional[Union[NameSpace, TypeInfo]]:
        r = self.params.get(name)
        if r: return r
        return self.parent.find_name(name)
    
    def register_name(self, name: Name, value: NameSpace) -> None:
        if self.sub_namespace is not None:
            raise AnalysisError('', self.pos, self.top_level)
        self.sub_namespace = value

@dataclass
class SingleBind(NameSpace, Positional):
    name: Name
    fullname: Name
    typedef: Union[NameSpace, TypeInfo]
    parent: NameSpace
    top_level: Module
    sub_namespace: List[NameSpace]

    def get_top_level(self) -> Module:
        return self.top_level
    
    def find_name(self, name: Name) -> Optional[Union[NameSpace, TypeInfo]]:
        '''
        时间复杂度O(n)\n
        EN: time complexity O(n)
        '''
        if self.name == name:
            return self.typedef
        return self.parent.find_name(name)
    
    def register_name(self, name: Name, value: NameSpace) -> None:
        self.sub_namespace.append(value)

@dataclass
class Scope(NameSpace, Positional):
    bind: Dict[Name, TypeInfo]
    parent: NameSpace
    top_level: Module
    sub_namespace: List[NameSpace]

    def get_top_level(self) -> Module:
        return self.top_level
    
    def find_name(self, name: Name) -> Optional[Union[NameSpace, TypeInfo]]:
        r = self.bind.get(name)
        if r: return r
        return self.parent.find_name(name)
    
    def register_name(self, name: Name, value: NameSpace) -> None:
        self.sub_namespace.append(value)

    def bind_typedef(self, name: Name, value: TypeInfo):
        self.bind[name] = value
