from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from enum import Flag
from enum import auto
from typing import Callable
from typing import Optional

from bytelang.content.impl.environments import Environment
from bytelang.content.impl.environments import EnvironmentInstruction
from bytelang.content.impl.primitives import PrimitiveType
from tools.reprtool import ReprTool


class Regex:
    IDENTIFIER = r"^[a-zA-Z_][a-zA-Z\d_]*$"
    CHAR = r"^'.'$"
    INTEGER = r"^0$|^([+-]?[1-9][\d_]*)$"
    EXPONENT = r"^[-+]?\d+[.]\d+([eE][-+]?\d+)?$"
    HEX_VALUE = r"^0[xX][_\da-fA-F]+$"
    OCT_VALUE = r"^[+-]?0[_0-7]+$"
    BIN_VALUE = r"^0[bB][_01]+$"

    NAME = r"[_a-zA-Z\d]+"


@dataclass(frozen=True, kw_only=True)
class Statement:
    type: StatementType
    line: str
    index: int
    head: str
    arguments: tuple[Optional[UniversalArgument], ...]

    def __str__(self) -> str:
        type_index = f"{self.type.name}{f'@{self.index}':<5}"
        heap_lexemes = self.head + (ReprTool.iter(self.arguments) if self.type is not StatementType.MARK_DECLARE else "")
        return f"{self.line:32} {type_index:32} {heap_lexemes}"


class StatementType(Enum):
    """Виды выражений"""

    DIRECTIVE_USE = f"[.]{Regex.NAME}"
    """Использование директивы"""
    MARK_DECLARE = f"{Regex.NAME}:"
    """Установка метки"""
    INSTRUCTION_CALL = Regex.NAME
    """Вызов инструкции"""

    def __repr__(self) -> str:
        return self.name


class ArgumentValueType(Flag):
    """Значения, которые есть в аргументе"""
    INTEGER = auto()
    EXPONENT = auto()
    IDENTIFIER = auto()

    NUMBER = INTEGER | EXPONENT
    ANY = IDENTIFIER | NUMBER


@dataclass(frozen=True, kw_only=True)
class UniversalArgument:
    """Универсальный тип для значения аргумента"""

    type: ArgumentValueType
    integer: Optional[int]
    exponent: Optional[float]
    identifier: Optional[str]

    @staticmethod
    def fromName(name: str) -> UniversalArgument:
        return UniversalArgument(type=ArgumentValueType.IDENTIFIER, integer=None, exponent=None, identifier=name)

    @staticmethod
    def fromInteger(value: int) -> UniversalArgument:
        return UniversalArgument(type=ArgumentValueType.NUMBER, integer=value, exponent=float(value), identifier=None)

    @staticmethod
    def fromExponent(value: float) -> UniversalArgument:
        return UniversalArgument(type=ArgumentValueType.NUMBER, integer=math.floor(value), exponent=value, identifier=None)

    def __repr__(self) -> str:
        if self.identifier is None:
            return f"{{ {self.integer} | {self.exponent} }}"

        return f"<{self.identifier}>"


@dataclass(frozen=True, kw_only=True)
class Variable:
    """Переменная программы"""

    address: int
    """адрес"""
    identifier: str
    """Идентификатор"""
    primitive: PrimitiveType
    """Примитивный тип"""
    value: bytes
    """Значение"""

    def write(self) -> bytes:
        return self.value

    def __repr__(self) -> str:
        return f"{self.primitive!s} {self.identifier}@{self.address} = {ReprTool.prettyBytes(self.value)}"


@dataclass(frozen=True)
class DirectiveArgument:
    """Параметры аргумента директивы"""

    name: str
    """Имя параметра (для вывода ошибок)"""
    type: ArgumentValueType
    """Маска принимаемых типов"""


@dataclass(frozen=True)
class Directive:
    """Конфигурация директивы"""

    handler: Callable[[Statement], None]
    """Обработчик директивы"""
    arguments: tuple[DirectiveArgument, ...]
    """Параметры аргументов."""


@dataclass(frozen=True, kw_only=True)
class ProgramData:
    environment: Environment
    start_address: int
    variables: tuple[Variable, ...]
    constants: dict[str, UniversalArgument]
    marks: dict[int, str]


@dataclass(frozen=True, kw_only=True)
class CodeInstruction:
    """Инструкция кода"""

    instruction: EnvironmentInstruction
    """Используемая инструкция"""
    arguments: tuple[bytes, ...]
    """Запакованные аргументы"""
    address: int
    """адрес расположения инструкции"""

    def write(self, instruction_index: PrimitiveType) -> bytes:
        return instruction_index.write(self.instruction.index) + b"".join(self.arguments)

    def __repr__(self) -> str:
        args_s = ReprTool.iter((f"({arg_t}){ReprTool.prettyBytes(arg_v)}" for arg_t, arg_v in zip(self.instruction.arguments, self.arguments)), l_paren="{ ", r_paren=" }")
        return f"{self.instruction.generalInfo()} {args_s}"
