from __future__ import annotations

from os import PathLike
from typing import BinaryIO
from typing import Optional
from typing import TextIO

from bytelang.code_generator import ByteCodeGenerator
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
from bytelang.result import CompileResult
from bytelang.result import CompileResult
from bytelang.source_generator import InstructionSourceGenerator
from bytelang.source_generator import Language
from bytelang.tools import FileTool

type AnyPath = str | PathLike


class ByteLang:
    """API byteLang"""

    def __init__(
            self,
            primitives_registry: PrimitivesRegistry,
            environment_registry: EnvironmentsRegistry
    ) -> None:
        self.__primitives_registry = primitives_registry

        self.__errors_handler = ErrorHandler()

        self.__parser = StatementParser(self.__errors_handler)
        self.__code_generator = CodeGenerator(self.__errors_handler, environment_registry, primitives_registry)
        self.__bytecode_generator = ByteCodeGenerator(self.__errors_handler)

    def compile(self, source_input_stream: TextIO, bytecode_output_stream: BinaryIO) -> Optional[CompileResult]:
        """Скомпилировать исходный код bls в байткод программу"""

        self.__errors_handler.reset()

        statements = tuple(self.__parser.run(source_input_stream))

        instructions, data = self.__code_generator.run(statements)

        bytecode = self.__bytecode_generator.run(instructions, data)

        if bytecode is None:
            return

        if not self.__errors_handler.success():
            return

        bytecode_output_stream.write(bytecode)

        return CompileResult(
            primitives=self.__primitives_registry.getValues(),
            statements=statements,
            instructions=instructions,
            program_data=data,
            bytecode=bytecode,
            source_filepath=str(source_input_stream.name),
            bytecode_filepath=str(bytecode_output_stream.name)
        )
