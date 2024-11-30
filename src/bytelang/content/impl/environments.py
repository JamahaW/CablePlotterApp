from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.content.abc import CatalogRegistry
from bytelang.content.abc import Content
from bytelang.content.impl.primitives import PrimitiveType
from bytelang.content.impl.profiles import Profile
from bytelang.content.impl.profiles import ProfileRegistry
from tools.filetool import FileTool
from tools.reprtool import ReprTool


@dataclass(frozen=True, kw_only=True)
class Environment(Content):
    """Окружение виртуальной машины"""

    profile: Profile
    """Профиль этого окружения (Настройки Виртуальной машины)"""
    instructions: dict[str, EnvironmentInstruction]
    """Инструкции окружения"""


@dataclass(frozen=True, kw_only=True)
class EnvironmentInstructionArgument:
    """Аргумент инструкции окружения"""

    SHAKE_CASE_POINTER_SUFFIX: Final[ClassVar[str]] = "_ptr"

    primitive_type: PrimitiveType
    """Подставляемое значение"""
    pointing_type: Optional[PrimitiveType]
    """На какой тип является указателем"""

    def __repr__(self) -> str:
        from bytelang.content.impl.packages import PackageInstructionArgument

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


class EnvironmentsRegistry(CatalogRegistry[Environment]):
    from bytelang.content.impl.packages import PackageRegistry

    def __init__(self, target_folder: Path, file_ext: str, profiles: ProfileRegistry, packages: PackageRegistry) -> None:
        super().__init__(target_folder, file_ext)
        self.__profiles = profiles
        self.__packages = packages

    def _load(self, filepath: Path, name: str) -> Environment:
        data = FileTool.readJSON(filepath)
        profile = self.__profiles.get(data["profile"])

        return Environment(
            parent=str(filepath),
            name=name,
            profile=profile,
            instructions=self.__processPackages(profile, data["packages"])
        )

    def __processPackages(self, profile: Profile, packages_names: Iterable[str]) -> dict[str, EnvironmentInstruction]:
        ret = dict[str, EnvironmentInstruction]()
        index: int = 0

        for package_name in packages_names:
            for ins in self.__packages.get(package_name).instructions:
                if (ex_ins := ret.get(ins.name)) is not None:
                    raise ValueError(f"{ins} - overload is not allowed ({ex_ins} defined already)")  # TODO add overload or namespaces

                ret[ins.name] = ins.transform(index, profile)
                index += 1

        return ret
