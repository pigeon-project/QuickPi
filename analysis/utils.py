from ast import AST

from typing import Any
from typing_extensions import ClassVar

Name = str

type_id_alloc: int = 0


def alloc_type_id() -> int:
    global type_id_alloc
    res = type_id_alloc
    type_id_alloc += 1
    return res


class PosInfo:
    lineno: ClassVar[int]
    col_offset: ClassVar[int]

    def __init__(self, ast: AST):
        self.lineno = ast.lineno
        self.col_offset = ast.col_offset


class AnalysisWarning(RuntimeWarning):
    message: ClassVar[str]
    pos: ClassVar[PosInfo]
    top_level: ClassVar

    def __init__(
            self,
            message: str,
            pos: PosInfo,
            top_level: Any
    ):
        self.message = message
        self.pos = pos
        self.top_level = top_level

    def __str__(self):
        return f'AnalysisWarning: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'


class AnalysisError(RuntimeError):
    message: ClassVar[str]
    pos: ClassVar[PosInfo]
    top_level: ClassVar

    def __init__(
            self,
            message: str,
            pos: PosInfo,
            top_level: Any
    ):
        self.message = message
        self.pos = pos
        self.top_level = top_level

    def __str__(self):
        return f'AnalysisError: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'


class TypeCheckError(AnalysisError):
    def __str__(self):
        return f'TypeCheckError: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'

