from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Final
from typing import Iterable
from typing import Optional
from typing import TextIO

from tools.filters import Filter


class Parser[T](ABC):
    """Базовый парсер bytelang"""

    COMMENT: Final[str] = "#"  # TODO move to syntax class

    def run(self, file: TextIO) -> Iterable[T]:
        return Filter.notNone(
            self._parseLine(index + 1, line)
            for index, line in enumerate(filter(bool, map(self.__cleanup, file)))
        )

    def __cleanup(self, line: str) -> str:
        return line.split(self.COMMENT)[0].strip()

    @abstractmethod
    def _parseLine(self, index: int, line: str) -> Optional[T]:
        """Обработать чистую строчку кода и вернуть абстрактный токен"""
