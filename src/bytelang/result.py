from __future__ import annotations

from dataclasses import dataclass
from enum import Flag
from enum import auto
from typing import BinaryIO
from typing import TextIO

from bytelang.code_generator import CodeInstruction
from bytelang.code_generator import ProgramData
from bytelang.parsers import Parser
from bytelang.statement import Statement
from bytelang.tools import ReprTool
from bytelang.tools import StringBuilder


# TODO выбрать подходящее название

# TODO Организовать флаги
class LogFlag(Flag):
    """Флаги вывода логов компиляции"""
    ENVIRONMENT_INSTRUCTIONS = auto()
    """Вывести инструкции окружения"""
    PROFILE = auto()
    """Вывести данные профиля"""
    REGISTRIES = ENVIRONMENT_INSTRUCTIONS | PROFILE
    """Вывести все доступные реестры"""

    STATEMENTS = auto()
    """Представление выражений"""
    CODE_INSTRUCTIONS = auto()
    """Представление инструкций промежуточного кода"""
    PARSER_RESULTS = CODE_INSTRUCTIONS | STATEMENTS
    """Весь парсинг"""

    VARIABLES = auto()
    """Представление переменных"""
    CONSTANTS = auto()
    """Значения констант"""
    PROGRAM_VALUES = VARIABLES | CONSTANTS
    """Все значения"""

    BYTECODE = auto()
    """Читаемый вид байт-кода"""

    ALL = REGISTRIES | PARSER_RESULTS | PROGRAM_VALUES | BYTECODE
    """Всё и сразу"""


@dataclass(frozen=True, kw_only=True, repr=False)
class CompileResultLegacy:
    statements: tuple[Statement, ...]
    instructions: tuple[CodeInstruction, ...]
    program_data: ProgramData

    source_stream: TextIO
    bytecode_stream: BinaryIO

    def getInfoLog(self, flags: LogFlag = LogFlag.ALL) -> str:
        sb = StringBuilder()
        env = self.program_data.environment

        if LogFlag.ENVIRONMENT_INSTRUCTIONS in flags:
            sb.append(ReprTool.headed(f"instructions : {env.name}", env.instructions.values()))

        if LogFlag.PROFILE in flags:
            sb.append(ReprTool.title(f"profile : {env.profile.name}")).append(ReprTool.strDict(env.profile.__dict__, _repr=True))

        if LogFlag.STATEMENTS in flags:
            sb.append(ReprTool.headed(f"statements : {self.source_stream.name}", self.statements))

        if LogFlag.CONSTANTS in flags:
            sb.append(ReprTool.title("constants")).append(ReprTool.strDict(self.program_data.constants))

        if LogFlag.VARIABLES in flags:
            sb.append(ReprTool.headed("variables", self.program_data.variables))

        if LogFlag.CODE_INSTRUCTIONS in flags:
            sb.append(ReprTool.headed(f"code instructions : {self.source_stream.name}", self.instructions))

        if LogFlag.BYTECODE in flags:
            self.__writeByteCode(sb)

        return sb.toString()

    @staticmethod
    def __writeComment(sb: StringBuilder, message: object) -> None:
        sb.append(f"\n{Parser.COMMENT}  {message}")

    def __writeByteCode(self, sb: StringBuilder) -> None:
        ins_by_addr = {ins.address: ins for ins in self.instructions}
        var_by_addr = {var.address: var for var in self.program_data.variables}

        sb.append(ReprTool.title(f"bytecode view : {self.bytecode_stream.name}"))
        self.bytecode_stream.close()

        with open(self.bytecode_stream.name, "rb") as bytecode_view:
            bytecode_view_read = bytecode_view.read()
            for address, byte in enumerate(bytecode_view_read):
                if address == 0:
                    self.__writeComment(sb, "program start address define")

                if (var := var_by_addr.get(address)) is not None:
                    self.__writeComment(sb, var)

                if (mark := self.program_data.marks.get(address)) is not None:
                    self.__writeComment(sb, f"{mark}:")

                if (ins := ins_by_addr.get(address)) is not None:
                    self.__writeComment(sb, ins)

                sb.append(f"{address:04X}: {byte:02X}")
