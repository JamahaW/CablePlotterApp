from enum import Enum
from typing import Callable

import qdarktheme
from PyQt6.QtWidgets import QComboBox


class EnumComboBox[E: Enum](QComboBox):

    def __init__(self, enum_class: type[E], on_select: Callable[[E], None]) -> None:
        super().__init__()
        self._options = {e.name.capitalize(): e for e in enum_class}
        self._option_names_by_enum = {e: name for name, e in self._options.items()}
        self.addItems(self._options.keys())
        # noinspection PyUnresolvedReferences
        self.currentTextChanged.connect(lambda name: on_select(self._options.get(name)))

    def setCurrent(self, e: E) -> None:
        self.setCurrentText(self._option_names_by_enum.get(e))


class ThemeComboBox(QComboBox):

    def __init__(self):
        super().__init__()
        self.addItems(qdarktheme.get_themes())
        # noinspection PyUnresolvedReferences
        self.currentTextChanged.connect(qdarktheme.setup_theme)
