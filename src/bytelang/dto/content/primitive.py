from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from struct import Struct
from typing import ClassVar

from bytelang.dto.content import Content


class PrimitiveWriteType(Enum):
    """Способ записи данных примитивного типа"""

    SIGNED = auto()
    UNSIGNED = auto()
    EXPONENT = auto()

    def __str__(self) -> str:
        return self.name.lower()


@dataclass(frozen=True, kw_only=True)
class PrimitiveType(Content):
    """Примитивный тип данных"""

    INTEGER_FORMATS: ClassVar[dict[int, str]] = {
        1: "B",
        2: "H",
        4: "I",
        8: "Q"
    }

    # TODO float16

    EXPONENT_FORMATS: ClassVar[dict[int, str]] = {
        4: "f",
        8: "d"
    }

    size: int
    """Размер примитивного типа"""
    write_type: PrimitiveWriteType
    """Способ записи"""
    packer: Struct
    """Упаковщик структуры"""

    def write(self, v: int | float) -> bytes:
        return self.packer.pack(v)

    def __repr__(self) -> str:
        return f"[{self.write_type} {self.size * 8}-bit] {self.__str__()}"

    def __str__(self) -> str:
        return f"{self.parent}::{self.name}"
