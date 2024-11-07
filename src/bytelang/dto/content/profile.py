from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bytelang.abc.content import Content
from bytelang.dto.content.primitive import PrimitiveType


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
