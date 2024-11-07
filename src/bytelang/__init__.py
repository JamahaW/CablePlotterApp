from __future__ import annotations

from os import PathLike
from typing import BinaryIO
from typing import Optional
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
from bytelang.result import CompileResult
from bytelang.result import CompileResult
from bytelang.source_generator import InstructionSourceGenerator
from bytelang.source_generator import Language
from bytelang.tools import FileTool

type AnyPath = str | PathLike


class ByteLang:
    """API byteLang"""

    def __init__(self, primitives_registry: PrimitivesRegistry, environment_registry: EnvironmentsRegistry) -> None:
        self.__primitives_registry = primitives_registry
        self.__environment_registry = environment_registry

    def compile(self, source_input_stream: TextIO, bytecode_output_stream: BinaryIO) -> Optional[CompileResult]:
        """Скомпилировать исходный код bls в байткод программу"""

        errors_handler = ErrorHandler()

        statements = tuple(StatementParser(errors_handler).run(source_input_stream))

        instructions, data = CodeGenerator(errors_handler, self.__environment_registry, self.__primitives_registry).run(statements)

        if data is None:
            errors_handler.write("Program data is None")
            return

        ByteCodeWriter(errors_handler).run(instructions, data, bytecode_output_stream)

        if not errors_handler.isSuccess():
            return

        return CompileResult(
            statements=statements,
            instructions=instructions,
            program_data=data,
            source_stream=source_input_stream,
            bytecode_stream=bytecode_output_stream
        )
