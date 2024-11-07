from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import BinaryIO
from typing import TextIO

from bytelang.code_generator import ByteCodeWriter
from bytelang.code_generator import CodeGenerator
from bytelang.content import Environment
from bytelang.handlers import BasicErrorHandler
from bytelang.handlers import ErrorHandler
from bytelang.interpreters import Interpreter
from bytelang.parsers import StatementParser
from bytelang.registries import EnvironmentsRegistry
from bytelang.registries import PackageRegistry
from bytelang.registries import PrimitivesRegistry
from bytelang.registries import ProfileRegistry
from bytelang.result import LogFlag
from bytelang.result import Result
from bytelang.result import ResultError
from bytelang.result import ResultOK

type AnyPath = str | PathLike


class ByteLang:
    """API byteLang"""

    @classmethod
    def simpleSetup(cls, bytelang_path: AnyPath) -> ByteLang:
        """
        Получить простую конфигурацию bytelang
        :param bytelang_path:
        :return: Рабочую конфигурацию ByteLang
        """
        bytelang_path = Path(bytelang_path)

        primitives_registry = PrimitivesRegistry(bytelang_path / "std.json")
        profile_registry = ProfileRegistry(bytelang_path / "profiles", "json", primitives_registry)
        package_registry = PackageRegistry(bytelang_path / "packages", "blp", primitives_registry)
        environments_registry = EnvironmentsRegistry(bytelang_path / "env", "json", profile_registry, package_registry)

        return ByteLang(primitives_registry, environments_registry)

    def __init__(self, primitives_registry: PrimitivesRegistry, environment_registry: EnvironmentsRegistry) -> None:
        self.__primitives_registry = primitives_registry
        self.__environment_registry = environment_registry

    def compile(self, source_input_stream: TextIO, bytecode_output_stream: BinaryIO, log_flags: LogFlag = LogFlag.ALL) -> Result:
        """
        Скомпилировать исходный код из источника в байткод на выходе
        :param log_flags: Уровень отображения сообщения компиляции
        :param source_input_stream: Источник исходного кода
        :param bytecode_output_stream: Выход байткода
        :return: Результат компиляции
        """

        errors_handler = ErrorHandler()
        error_result = ResultError(source_input_stream, bytecode_output_stream, errors_handler)

        statements = tuple(StatementParser(errors_handler).run(source_input_stream))

        if not errors_handler.isSuccess():
            return error_result

        instructions, program_data = CodeGenerator(errors_handler, self.__environment_registry, self.__primitives_registry).run(statements)

        if program_data is None:
            errors_handler.write("Program data is None")
            return error_result

        ByteCodeWriter(errors_handler).run(instructions, program_data, bytecode_output_stream)

        if not errors_handler.isSuccess():
            return error_result

        return ResultOK(source_input_stream, bytecode_output_stream, log_flags, statements, instructions, program_data)
