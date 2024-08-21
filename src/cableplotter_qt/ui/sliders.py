from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QWidget

from cableplotter_qt.ui.displays import ValueDisplay


class NamedSlider(QWidget):

    def __init__(self, name: str, slider: QSlider) -> None:
        super().__init__()
        self.slider = slider
        self.label = ValueDisplay(name, slider.value())

        # noinspection PyUnresolvedReferences
        self.slider.valueChanged.connect(self.label.updateValue)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def value(self) -> int:
        return self.slider.value()


class Slider(QSlider):

    def __init__(self, max_value: int, min_value: int = 0, on_change: Callable[[int], None] = None, step: int = 1) -> None:
        super().__init__(Qt.Orientation.Horizontal)
        self.setRange(min_value, max_value)
        self.setSingleStep(step)

        if on_change:
            # noinspection PyUnresolvedReferences
            self.valueChanged.connect(on_change)
