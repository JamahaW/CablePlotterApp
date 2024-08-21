from typing import Callable

from PyQt6.QtWidgets import QSpinBox


class UnitSpinBox(QSpinBox):

    def __init__(self, unit: str, step: int, on_change: Callable[[int], None] = None) -> None:
        super().__init__()
        self.setSuffix(unit)
        self.setSingleStep(step)
        self.setRange(0, 10000)

        if on_change is not None:
            # noinspection PyUnresolvedReferences
            self.valueChanged.connect(on_change)
