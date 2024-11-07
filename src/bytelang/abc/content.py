from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Content:
    """Абстрактный контент, загружаемый реестрами"""

    parent: str
    """Родительский контент"""
    name: str
    """Наименование контента"""
