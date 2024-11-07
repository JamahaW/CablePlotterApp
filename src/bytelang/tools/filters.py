from __future__ import annotations

from typing import Iterable
from typing import Optional


class Filter:

    @staticmethod
    def notNone[T](i: Iterable[Optional[T]]) -> Iterable[T]:
        return filter(None.__ne__, i)
