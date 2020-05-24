from typing import TypeVar

from .utils import Name


class TypeInfo:
    def __init__(self):
        pass


class TypeRef(TypeInfo):
    name: TypeVar[Name]

    def __init__(self, name: Name):
        super().__init__()
        self.name = name


"""
class AliasType(TypeInfo):
    pass
"""


class ProperType(TypeInfo):
    pass


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
