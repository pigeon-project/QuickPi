from typing import Any
from typing_extensions import ClassVar
from dataclasses import dataclass
from ast import AST

Name = str

type_id_alloc: int = 0


def alloc_type_id() -> int:
    '''
    分配类型ID\n
    EN: alloc type id
    '''
    global type_id_alloc
    res = type_id_alloc
    type_id_alloc += 1
    return res

def intersection(a, b):
    '''
    为了通过reduce类型检查写的一个辅助函数\n
    EN: unimportant
    '''
    return a.intersection(b)


def trait(i: type):
    '''
    将class注释为trait\n
    EN: Annotate the class as Trait
    '''
    return i


@dataclass
class PosInfo:
    lineno: int
    col_offset: int


@dataclass
class AnalysisWarning(RuntimeWarning):
    message: str
    pos: PosInfo
    top_level: Any

    def __str__(self):
        return f'AnalysisWarning: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'


@dataclass
class AnalysisError(RuntimeError):
    message: str
    pos: PosInfo
    top_level: Any

    def __str__(self):
        return f'AnalysisError: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'


class TypeCheckError(AnalysisError):
    def __str__(self):
        return f'TypeCheckError: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'

class TypeNonUnifyError(RuntimeError):...
