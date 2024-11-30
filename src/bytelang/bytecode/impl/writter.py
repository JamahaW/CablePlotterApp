from __future__ import annotations

from struct import error
from typing import BinaryIO
from typing import Iterable

from bytelang.bytecode.abc import CodeInstruction
from bytelang.bytecode.abc import ProgramData
from bytelang.content.impl.profiles import Profile
from bytelang.core.handlers.errors import BasicErrorHandler
from bytelang.utils import CountingStream


class ByteCodeWriter:

    def __init__(self, error_handler: BasicErrorHandler) -> None:
        self.__error_handler = error_handler.getChild(self.__class__.__name__)

    def run(self, instructions: Iterable[CodeInstruction], program_data: ProgramData, bytecode_output_stream: BinaryIO) -> int:
        profile = program_data.environment.profile
        out = CountingStream(bytecode_output_stream)

        self.__writeStartBlock(out, program_data)
        self.__writeVariablesBlock(out, program_data)
        self.__writeInstructionsBlock(out, instructions, profile)

        self.__checkProgram(out, profile)
        return out.getBytesWritten()

    def __writeStartBlock(self, out: CountingStream, program_data: ProgramData) -> None:
        try:
            program_start_data = program_data.environment.profile.pointer_heap.write(program_data.start_address)
            out.write(program_start_data)

        except error as e:
            self.__error_handler.write(f"Область Heap вне допустимого размера: {e}")

    def __checkProgram(self, out: CountingStream, profile: Profile) -> None:
        if profile.max_program_length is None:
            return

        if out.getBytesWritten() < profile.max_program_length:
            return

        self.__error_handler.write(f"program size ({out.getBytesWritten()}) out of {profile.max_program_length}")

    @staticmethod
    def __writeInstructionsBlock(out: CountingStream, instructions: Iterable[CodeInstruction], profile: Profile):
        out.write(b"".join(map(lambda ins: ins.write(profile.instruction_index), instructions)))

    @staticmethod
    def __writeVariablesBlock(out: CountingStream, program_data: ProgramData) -> None:
        out.write(b"".join(map(lambda v: v.value, program_data.variables)))
