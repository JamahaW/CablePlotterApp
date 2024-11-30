from __future__ import annotations

from enum import Flag
from enum import auto
from typing import AnyStr
from typing import IO


class LogFlag(Flag):
    # TODO выбрать подходящее название
    # TODO Организовать флаги
    """Флаги вывода логов компиляции"""
    PRIMITIVES = auto()
    """Вывести данные реестра примитивных типов"""
    ENVIRONMENT_INSTRUCTIONS = auto()
    """Вывести инструкции окружения"""
    PROFILE = auto()
    """Вывести данные профиля"""
    REGISTRIES = PRIMITIVES | ENVIRONMENT_INSTRUCTIONS | PROFILE
    """Вывести все доступные реестры"""

    STATEMENTS = auto()
    """Представление выражений"""
    CODE_INSTRUCTIONS = auto()
    """Представление инструкций промежуточного кода"""
    PARSER_RESULTS = CODE_INSTRUCTIONS | STATEMENTS
    """Весь парсинг"""

    COMPILATION_TIME = auto()
    """Длительность компиляции"""

    PROGRAM_SIZE = auto()
    """Размер программы в байтах"""
    VARIABLES = auto()
    """Представление переменных"""
    CONSTANTS = auto()
    """Значения констант"""
    PROGRAM_VALUES = VARIABLES | CONSTANTS | PROGRAM_SIZE
    """Все значения"""

    BYTECODE = auto()
    """Читаемый вид байт-кода"""

    ALL = REGISTRIES | PARSER_RESULTS | PROGRAM_VALUES | BYTECODE
    """Всё и сразу"""


class CountingStream:

    def __init__(self, stream: IO) -> None:
        self.__stream = stream
        self.__bytes_written = 0

    def write(self, data: AnyStr) -> None:
        self.__stream.write(data)
        self.__bytes_written += len(data)

    def getBytesWritten(self) -> int:
        return self.__bytes_written
