from __future__ import annotations

from dataclasses import dataclass

from bytelang.dto.content import Content
from bytelang.dto.content.instructions import EnvironmentInstruction
from bytelang.dto.content.profile import Profile


@dataclass(frozen=True, kw_only=True)
class Environment(Content):
    """Окружение виртуальной машины"""

    profile: Profile
    """Профиль этого окружения (Настройки Виртуальной машины)"""
    instructions: dict[str, EnvironmentInstruction]
    """Инструкции окружения"""
