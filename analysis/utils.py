from ast import AST
from typing_extensions import ClassVar

from .mata_info import ModuleMataInfo

Name = str


class PosInfo:
    lineno: ClassVar[int]
    col_offset: ClassVar[int]

    def __init__(self, ast: AST):
        self.lineno = ast.lineno
        self.col_offset = ast.col_offset


class AnalysisError(RuntimeError):
    message: ClassVar[str]
    pos: ClassVar[PosInfo]
    top_level: ClassVar[ModuleMataInfo]

    def __init__(
            self,
            message: str,
            pos: PosInfo,
            top_level: ModuleMataInfo
    ):
        self.message = message
        self.pos = pos
        self.top_level = top_level

    def __str__(self):
        return f'AnalysisError: "{self.message}"\n' \
               f'\t File "{self.top_level.fullname}", line {self.pos.lineno}, col {self.pos.col_offset}'

