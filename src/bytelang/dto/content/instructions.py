from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from typing import Final
from typing import Optional

from bytelang.abc.content import Content
from bytelang.dto.content.primitive import PrimitiveType
from bytelang.dto.content.profile import Profile
from bytelang.tools import ReprTool


@dataclass(frozen=True, kw_only=True)
class PackageInstructionArgument:
    """Аргумент инструкции"""

    POINTER_CHAR: Final[ClassVar[str]] = "*"

    primitive: PrimitiveType
    """Примитивный тип аргумента"""
    is_pointer: bool
    """Если указатель - значение переменной будет считано как этот тип"""

    def __repr__(self) -> str:
        return f"{self.primitive.__str__()}{self.POINTER_CHAR * self.is_pointer}"

    def transform(self, profile: Profile) -> EnvironmentInstructionArgument:
        """Получить аргумент инструкции окружения с актуальным примитивным типом значения на основе профиля."""
        if not self.is_pointer:
            return EnvironmentInstructionArgument(primitive_type=self.primitive, pointing_type=None)

        return EnvironmentInstructionArgument(primitive_type=profile.pointer_heap, pointing_type=self.primitive)


@dataclass(frozen=True, kw_only=True)
class PackageInstruction(Content):
    """Базовые сведения об инструкции"""

    arguments: tuple[PackageInstructionArgument, ...]
    """Аргументы базовой инструкции"""

    def __repr__(self) -> str:
        return f"{self.parent}::{self.name}{ReprTool.iter(self.arguments)}"

    def transform(self, index: int, profile: Profile) -> EnvironmentInstruction:
        """Создать инструкцию окружения на основе базовой и профиля"""
        args = tuple(arg.transform(profile) for arg in self.arguments)
        size = profile.instruction_index.size + sum(arg.primitive_type.size for arg in args)
        return EnvironmentInstruction(
            parent=profile.name,
            name=self.name,
            index=index,
            package=self.parent,
            arguments=args,
            size=size
        )


@dataclass(frozen=True, kw_only=True)
class EnvironmentInstructionArgument:
    """Аргумент инструкции окружения"""

    SHAKE_CASE_POINTER_SUFFIX: Final[ClassVar[str]] = "_ptr"

    primitive_type: PrimitiveType
    """Подставляемое значение"""
    pointing_type: Optional[PrimitiveType]
    """На какой тип является указателем"""

    def __repr__(self) -> str:
        if self.pointing_type is None:
            return self.primitive_type.__str__()

        return f"{self.primitive_type!s}{PackageInstructionArgument.POINTER_CHAR}({self.pointing_type!s})"

    def reprShakeCase(self) -> str:
        if self.pointing_type is None:
            return self.primitive_type.name

        return self.pointing_type.name + self.SHAKE_CASE_POINTER_SUFFIX


@dataclass(frozen=True, kw_only=True)
class EnvironmentInstruction(Content):
    """Инструкция окружения"""

    index: int
    """Индекс этой инструкции"""
    package: str
    """Пакет этой команды"""
    arguments: tuple[EnvironmentInstructionArgument, ...]
    """Аргументы окружения. Если тип был указателем, примитивный тип стал соответствовать типу указателя профиля окружения"""
    size: int
    """Размер инструкции в байтах"""

    def generalInfo(self) -> str:
        return f"[{self.size}B] {self.package}::{self.name}@{self.index}"

    def reprShakeCase(self) -> str:
        return f"__{self.parent}_{self.package}_{self.name}__{'__'.join(a.reprShakeCase() for a in self.arguments)}"

    def __repr__(self) -> str:
        return f"{self.generalInfo()}{ReprTool.iter(self.arguments)}"
