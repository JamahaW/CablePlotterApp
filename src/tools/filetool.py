from __future__ import annotations
from __future__ import annotations

import json
from os import PathLike
from os import PathLike
from pathlib import Path
from typing import Type


class FileTool:
    """Обёртка для работы с файлами"""

    @classmethod
    def read(cls, filepath: str | PathLike) -> str:
        with open(filepath, "rt") as f:
            return f.read()

    @classmethod
    def readBytes(cls, filepath: str | PathLike) -> bytes:
        with open(filepath, "rb") as f:
            return f.read()

    @classmethod
    def readJSON(cls, filepath: str | PathLike) -> dict | list:
        with open(filepath) as f:
            return json.load(f)

    @classmethod
    def save(cls, filepath: str | PathLike, _data: str):
        with open(filepath, "wt") as f:
            f.write(_data)

    @classmethod
    def saveBytes(cls, filepath: str | PathLike, _data: bytes):
        with open(filepath, "wb") as f:
            f.write(_data)


AnyPath = Type[str | PathLike]
