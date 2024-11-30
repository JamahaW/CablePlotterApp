from __future__ import annotations

from dataclasses import dataclass

from bytelang.bytecode.abc import CodeInstruction
from bytelang.core.handlers.errors import ErrorHandler
from bytelang.parsers.abc import Parser
from bytelang.bytecode.abc import ProgramData
from bytelang.bytecode.abc import Statement
from bytelang.results.abc import CompileResult
from bytelang.utils import LogFlag
from tools.reprtool import ReprTool
from tools.string import StringBuilder


@dataclass(frozen=True, repr=False)
class CompileResultOK(CompileResult):
    flags: LogFlag

    statements: tuple[Statement, ...]
    instructions: tuple[CodeInstruction, ...]
    program_data: ProgramData
    program_size: int
    compilation_time_seconds: float

    def isOK(self) -> bool:
        return True

    def getMessage(self) -> str:
        sb = StringBuilder()
        env = self.program_data.environment

        if LogFlag.ENVIRONMENT_INSTRUCTIONS in self.flags:
            sb.append(ReprTool.headed(f"instructions : {env.name}", env.instructions.values()))

        if LogFlag.PROFILE in self.flags:
            sb.append(ReprTool.title(f"profile : {env.profile.name}")).append(ReprTool.strDict(env.profile.__dict__, _repr=True))

        if LogFlag.STATEMENTS in self.flags:
            sb.append(ReprTool.headed(f"statements : {self.source_stream.name}", self.statements))

        if LogFlag.CONSTANTS in self.flags:
            sb.append(ReprTool.title("constants")).append(ReprTool.strDict(self.program_data.constants))

        if LogFlag.VARIABLES in self.flags:
            sb.append(ReprTool.headed("variables", self.program_data.variables))

        if LogFlag.CODE_INSTRUCTIONS in self.flags:
            sb.append(ReprTool.headed(f"code instructions : {self.source_stream.name}", self.instructions))

        if LogFlag.BYTECODE in self.flags:
            self.__writeByteCode(sb)

        if LogFlag.PROGRAM_SIZE in self.flags:
            sb.append(ReprTool.title(f"Program Size : {self.program_size} Bytes"))

        if LogFlag.COMPILATION_TIME in self.flags:
            sb.append(ReprTool.title(f"Compilation Time : {self.compilation_time_seconds:.02} seconds"))

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


@dataclass(frozen=True, repr=False)
class CompileResultError(CompileResult):
    error_handler: ErrorHandler

    def isOK(self) -> bool:
        return False

    def getMessage(self) -> str:
        return self.error_handler.getLog()
