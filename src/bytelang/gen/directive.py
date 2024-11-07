from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bytelang.impl.parsers.statement.statement import ArgumentValueType
from bytelang.impl.parsers.statement.statement import Statement


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
