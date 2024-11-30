from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from pathlib import Path
from struct import Struct
from typing import ClassVar

from bytelang.content.abc import Content
from bytelang.content.abc import JSONFileRegistry


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


_PrimitiveRaw = dict[str, int | str]


class PrimitivesRegistry(JSONFileRegistry[_PrimitiveRaw, PrimitiveType]):
    """Реестр примитивных типов"""

    def __init__(self, path: Path):
        """
        Реестр примитивных типов
        :param path: Путь к JSON файлу
        """
        self._primitives_by_size = dict[tuple[int, PrimitiveWriteType], PrimitiveType]()
        super().__init__(path)

    def getBySize(self, size: int, write_type: PrimitiveWriteType = PrimitiveWriteType.UNSIGNED) -> PrimitiveType:
        return self._primitives_by_size[size, write_type]

    def _parse(self, name: str, raw: _PrimitiveRaw) -> PrimitiveType:
        size = raw["size"]
        write_type = PrimitiveWriteType[raw["type"].upper()]

        # TODO исправить

        if (size, write_type) in self._primitives_by_size.keys():
            raise ValueError(f"type aliases not support: {name}, {raw}")

        formats = PrimitiveType.EXPONENT_FORMATS if write_type == PrimitiveWriteType.EXPONENT else PrimitiveType.INTEGER_FORMATS

        if (fmt := formats.get(size)) is None:
            raise ValueError(f"Invalid size ({size}) must be in {tuple(formats.keys())}")

        if write_type == PrimitiveWriteType.SIGNED:
            fmt = fmt.lower()

        ret = self._primitives_by_size[size, write_type] = PrimitiveType(
            name=name,
            parent=self._target_file.stem,
            size=size,
            write_type=write_type,
            packer=Struct(fmt)
        )

        return ret
