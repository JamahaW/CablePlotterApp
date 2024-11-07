from __future__ import annotations

from dataclasses import dataclass

from bytelang.dto.content.instructions import EnvironmentInstruction
from bytelang.dto.content.primitive import PrimitiveType
from bytelang.tools.reprtool import ReprTool


@dataclass(frozen=True, kw_only=True)
class CodeInstruction:
    """Инструкция кода"""

    instruction: EnvironmentInstruction
    """Используемая инструкция"""
    arguments: tuple[bytes, ...]
    """Запакованные аргументы"""
    address: int
    """адрес расположения инструкции"""

    def write(self, instruction_index: PrimitiveType) -> bytes:
        return instruction_index.write(self.instruction.index) + b"".join(self.arguments)

    def __repr__(self) -> str:
        args_s = ReprTool.iter((f"({arg_t}){ReprTool.prettyBytes(arg_v)}" for arg_t, arg_v in zip(self.instruction.arguments, self.arguments)), l_paren="{ ", r_paren=" }")
        return f"{self.instruction.generalInfo()} {args_s}"
