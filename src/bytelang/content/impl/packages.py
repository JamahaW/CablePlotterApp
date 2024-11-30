from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from typing import Final
from typing import Optional

from bytelang.content.abc import CatalogRegistry
from bytelang.content.abc import Content
from bytelang.content.impl.primitives import PrimitiveType
from bytelang.content.impl.primitives import PrimitivesRegistry
from bytelang.content.impl.environments import EnvironmentInstruction
from bytelang.content.impl.environments import EnvironmentInstructionArgument
from bytelang.parsers.abc import Parser
from bytelang.content.impl.profiles import Profile
from tools.reprtool import ReprTool


@dataclass(frozen=True, kw_only=True)
class Package(Content):
    """Пакет инструкций"""

    instructions: tuple[PackageInstruction, ...]
    """Набор инструкций"""


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


class PackageParser(Parser[PackageInstruction]):
    """Парсер пакета инструкций"""

    def __init__(self, primitives: PrimitivesRegistry):
        self.__used_names = set[str]()
        self.__package_name: Optional[str] = None
        self.__primitive_type_registry = primitives

    def begin(self, package_name: str) -> None:
        self.__package_name = package_name

    def _parseLine(self, index: int, line: str) -> Optional[PackageInstruction]:
        name, *arg_types = line.split()

        # TODO add override?

        if name in self.__used_names:
            raise ValueError(f"redefinition of {self.__package_name}::{name}{ReprTool.iter(arg_types)} at line {index} ")

        self.__used_names.add(name)

        return PackageInstruction(
            parent=self.__package_name,
            name=name,
            arguments=tuple(
                self.__parseArgument(self.__package_name, name, i, arg)
                for i, arg in enumerate(arg_types)
            )
        )

    def __parseArgument(self, package_name: str, name: str, index: int, arg_lexeme: str) -> PackageInstructionArgument:
        is_pointer = arg_lexeme[-1] == PackageInstructionArgument.POINTER_CHAR
        arg_lexeme = arg_lexeme.rstrip(PackageInstructionArgument.POINTER_CHAR)

        if (primitive := self.__primitive_type_registry.get(arg_lexeme)) is None:
            raise ValueError(f"Unknown primitive '{arg_lexeme}' at {index} in {package_name}::{name}")

        return PackageInstructionArgument(primitive=primitive, is_pointer=is_pointer)


class PackageRegistry(CatalogRegistry[Package]):

    def __init__(self, target_folder: Path, file_ext: str, primitives: PrimitivesRegistry):
        super().__init__(target_folder, file_ext)
        self.__parser = PackageParser(primitives)

    def _load(self, filepath: Path, name: str) -> Package:
        self.__parser.begin(name)

        with open(filepath) as f:
            return Package(parent=str(filepath), name=name, instructions=tuple(self.__parser.run(f)))
