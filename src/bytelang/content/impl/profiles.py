from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bytelang.content.abc import CatalogRegistry
from bytelang.content.abc import Content
from bytelang.content.impl.primitives import PrimitiveType
from bytelang.content.impl.primitives import PrimitivesRegistry
from tools.filetool import FileTool


@dataclass(frozen=True, kw_only=True)
class Profile(Content):
    """Профиль виртуальной машины"""

    max_program_length: Optional[int]
    """Максимальный размер программы. None, если неограничен"""
    pointer_program: PrimitiveType
    """Тип указателя программы (Определяет максимально возможный адрес инструкции)"""
    pointer_heap: PrimitiveType
    """Тип указателя кучи (Определяет максимально возможный адрес переменной"""
    instruction_index: PrimitiveType
    """Тип индекса инструкции (Определяет максимальное кол-во инструкций в профиле"""


class ProfileRegistry(CatalogRegistry[Profile]):

    def __init__(self, target_folder: Path, file_ext: str, primitives: PrimitivesRegistry):
        super().__init__(target_folder, file_ext)
        self.__primitive_type_registry = primitives

    def _load(self, filepath: str, name: str) -> Profile:
        data = FileTool.readJSON(filepath)

        def getType(t: str) -> PrimitiveType:
            return self.__primitive_type_registry.getBySize(data[t])

        return Profile(
            parent=filepath,
            name=name,
            max_program_length=data.get("prog_len"),
            pointer_program=getType("ptr_prog"),
            pointer_heap=getType("ptr_heap"),
            instruction_index=getType("ptr_inst"),
        )
