from __future__ import annotations

import time
from pathlib import Path
from typing import BinaryIO
from typing import Final
from typing import TextIO

from bytelang.bytecode.impl.gen import CodeGenerator
from bytelang.bytecode.impl.writter import ByteCodeWriter
from bytelang.content.impl.environments import EnvironmentsRegistry
from bytelang.content.impl.packages import PackageRegistry
from bytelang.content.impl.primitives import PrimitivesRegistry
from bytelang.content.impl.profiles import ProfileRegistry
from bytelang.core.handlers.errors import ErrorHandler
from bytelang.parsers.impl.statement import StatementParser
from bytelang.results.abc import CompileResult
from bytelang.results.impl import CompileResultError
from bytelang.results.impl import CompileResultOK
from bytelang.utils import LogFlag
from tools.filetool import AnyPath


class ByteLang:
    """API byteLang"""

    PACKAGE_EXTENSION: Final[str] = "blp"
    SOURCE_EXTENSION: Final[str] = "bls"
    BYTECODE_EXTENSION: Final[str] = "blc"

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
        package_registry = PackageRegistry(bytelang_path / "packages", cls.PACKAGE_EXTENSION, primitives_registry)
        environments_registry = EnvironmentsRegistry(bytelang_path / "env", "json", profile_registry, package_registry)

        return ByteLang(primitives_registry, environments_registry)

    def __init__(self, primitives_registry: PrimitivesRegistry, environment_registry: EnvironmentsRegistry) -> None:
        self.__primitives_registry = primitives_registry
        self.__environment_registry = environment_registry

    def compile(self, source_input_stream: TextIO, bytecode_output_stream: BinaryIO, log_flags: LogFlag = LogFlag.ALL) -> CompileResult:
        """
        Скомпилировать исходный код из источника в байт-код на выходе
        :param log_flags: Уровень отображения сообщения компиляции
        :param source_input_stream: Источник исходного кода
        :param bytecode_output_stream: Выход байт-кода
        :return: Результат компиляции
        """

        start_time = time.time()

        errors_handler = ErrorHandler()
        error_result = CompileResultError(source_input_stream, bytecode_output_stream, errors_handler)

        statements = tuple(StatementParser(errors_handler).run(source_input_stream))

        if not errors_handler.isSuccess():
            return error_result

        instructions, program_data = CodeGenerator(errors_handler, self.__environment_registry, self.__primitives_registry).run(statements)

        if program_data is None:
            errors_handler.write("Program data is None")
            return error_result

        program_size = ByteCodeWriter(errors_handler).run(instructions, program_data, bytecode_output_stream)

        if not errors_handler.isSuccess():
            return error_result

        compilation_time_seconds = time.time() - start_time

        return CompileResultOK(source_input_stream, bytecode_output_stream, log_flags, statements, instructions, program_data, program_size, compilation_time_seconds)
