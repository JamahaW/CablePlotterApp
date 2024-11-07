from __future__ import annotations

from struct import error
from typing import AnyStr
from typing import BinaryIO
from typing import IO
from typing import Iterable

from bytelang.dto.content.profile import Profile
from bytelang.gen.instruction import CodeInstruction
from bytelang.gen.code_generator import ProgramData
from bytelang.handlers.error import BasicErrorHandler


class CountingStream:

    def __init__(self, stream: IO) -> None:
        self.__stream = stream
        self.__bytes_written = 0

    def write(self, data: AnyStr) -> None:
        self.__stream.write(data)
        self.__bytes_written += len(data)

    def getBytesWritten(self) -> int:
        return self.__bytes_written


class ByteCodeWriter:

    def __init__(self, error_handler: BasicErrorHandler) -> None:
        self.__error_handler = error_handler.getChild(self.__class__.__name__)

    def run(self, instructions: Iterable[CodeInstruction], program_data: ProgramData, bytecode_output_stream: BinaryIO) -> None:
        profile = program_data.environment.profile
        out = CountingStream(bytecode_output_stream)

        self.__writeStartBlock(out, program_data)
        self.__writeVariablesBlock(out, program_data)
        self.__writeInstructionsBlock(out, instructions, profile)

        self.__checkProgram(out, profile)

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
