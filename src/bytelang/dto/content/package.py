from __future__ import annotations

from dataclasses import dataclass

from bytelang.dto.content import Content
from bytelang.dto.content.instructions import PackageInstruction


@dataclass(frozen=True, kw_only=True)
class Package(Content):
    """Пакет инструкций"""

    instructions: tuple[PackageInstruction, ...]
    """Набор инструкций"""
