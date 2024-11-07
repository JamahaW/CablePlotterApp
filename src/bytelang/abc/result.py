from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO
from typing import TextIO


@dataclass(frozen=True, repr=False)
class Result:
    """Результат работы компилятора ByteLang"""

    source_stream: TextIO
    bytecode_stream: BinaryIO

    def isOK(self) -> bool:
        """Получить статус"""

    def getMessage(self) -> str:
        """Получить сообщение результата"""
