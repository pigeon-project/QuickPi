from typing import List, Set, Iterable, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from functools import reduce
from ast import AST
from pathlib import Path

from .utils import trait, Name, intersection, AnalysisError


@trait
class TypeInfo:
    def join(self, other: 'TypeInfo') -> 'UnionType':
        return UnionType({self, other})
    def get_true_type(self) -> 'TypeInfo':
        return self

    def get_traits(self) -> Set['TraitInfo']: ...

@trait
class TraitInfo(TypeInfo):
    def get_traits(self) -> Set['TraitInfo']:
        return {self}


@dataclass
class UnionType(TypeInfo):
    value: Set[TypeInfo]

    def join(self, other: TypeInfo) -> 'UnionType':
        if isinstance(other, UnionType):
            o: Set[TypeInfo] = other.value
        o = {other}
        return UnionType(self.value | o)

    def get_traits(self) -> Set[TraitInfo]:
        if len(self.value) == 0: return set()
        traits_list = [i.get_traits() for i in self.value]
        return set(reduce(intersection, traits_list))


@trait
class NameSpace:
    def get_top_level(self) -> 'NameSpace': ...
    def find_name(self, name: Name) -> Optional[NameSpace]: ...
    def register_name(self, name: Name, value: NameSpace) -> 'NameSpace': ...

@dataclass
class Module(NameSpace):
    name: Name
    fullname: Name
    path: Path
    import_list: Dict[Name, NameSpace]
    bind: Dict[Name, NameSpace]

    def get_top_level(self) -> NameSpace:
        return self

    def find_name(self, name: Name) -> Optional[NameSpace]:
        r = self.bind.get(name)
        if r:
            return r
        return self.import_list.get(name)
    
    def register_name(self, name: Name, value: NameSpace) -> NameSpace:
        self.bind[name] = value
        return self


@dataclass
class Function(NameSpace):
    name: Name
    fullname: Name
    is_async: bool
    is_pure: Optional[bool]
    # type_vars: Dict[Name, QTypeVar]
    params: Dict[Name, Tuple[TypeInfo, Optional[AST]]] # (name: type = construct_expr, ...)
    throw: Optional[TypeInfo]
    sub_namespace: Optional[NameSpace]
    body: List[AST]
    parent: NameSpace
    top_level: Module

    def get_top_level(self) -> NameSpace:
        return self.top_level

    def find_name(self, name: Name) -> Optional[NameSpace]:
        r = self.params.get(name)
        if r:
            return SingleBind(
                name, f'{self.fullname}.<local>.{name}',
                r[0],
                self, self.top_level)
        return self.parent.find_name(name)
    
    def register_name(self, name: Name, value: NameSpace) -> NameSpace:
        if self.sub_namespace is not None:
            raise AnalysisError('', ..., self.top_level)
        r = SingleBind(
            name, f'{self.fullname}.<local>.{name}',
            value,
            self, self.top_level)
        self.sub_namespace = r
        return r

@dataclass
class SingleBind(NameSpace):
    name: Name
    fullname: Name
    typedef: Union[NameSpace, TypeInfo]
    parent: NameSpace
    top_level: Module

    def get_top_level(self) -> NameSpace:
        return self.top_level