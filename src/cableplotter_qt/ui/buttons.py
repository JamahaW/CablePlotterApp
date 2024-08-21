from typing import Callable

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton


class Button(QPushButton):

    def __init__(self, text: str, on_click: Callable[[], None], icon: QIcon = None) -> None:
        super().__init__(text)
        self.setMinimumWidth(180)

        # noinspection PyUnresolvedReferences
        self.clicked.connect(on_click)

        if icon is not None:
            self.setIcon(icon)
