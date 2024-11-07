"""
Различные Реестры контента
"""

from pathlib import Path
from struct import Struct
from typing import Iterable
from typing import Optional

from bytelang.abc.registries import CatalogRegistry
from bytelang.abc.registries import JSONFileRegistry
from bytelang.dto.content.environment import Environment
from bytelang.dto.content.instructions import EnvironmentInstruction
from bytelang.dto.content.package import Package
from bytelang.dto.content.instructions import PackageInstruction
from bytelang.dto.content.instructions import PackageInstructionArgument
from bytelang.dto.content.primitive import PrimitiveType
from bytelang.dto.content.primitive import PrimitiveWriteType
from bytelang.dto.content.profile import Profile
from bytelang.parsers import Parser
from bytelang.tools import FileTool
from bytelang.tools import ReprTool

# TODO сделать каталоговым реестром и файл как namespace

type _PrimitiveRaw = dict[str, int | str]


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


class EnvironmentsRegistry(CatalogRegistry[Environment]):

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
