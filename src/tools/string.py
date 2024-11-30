from __future__ import annotations

from io import StringIO


class FixedStringIO(StringIO):
    @property
    def name(self) -> str:
        return self.__class__.__name__


class StringBuilder(FixedStringIO):

    def __init__(self) -> None:
        super().__init__()

    def append(self, obj: object, end: str = "\n") -> StringBuilder:
        self.write(obj.__str__())
        self.write(end)
        return self

    def __str__(self) -> str:
        return self.getvalue()

    def toString(self) -> str:
        return self.__str__()
