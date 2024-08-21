from PyQt6.QtWidgets import QBoxLayout
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QVBoxLayout

from cableplotter_qt.app.tabs.imageprocessor import ImageProcessorTab
from cableplotter_qt.ui.buttons import Button
from cableplotter_qt.ui.dialogs import FileDialog
from cableplotter_qt.ui.displays import ImageDisplay
from cableplotter_qt.ui.scrollbars import VerticalScroll
from cableplotter_qt.ui.spinboxes import UnitSpinBox
from cableplotter_qt.ui.tab import Tab
from cableplotter_qt.ui.tab import TabWidget


class WorkFieldFrame(QFrame):

    def __init__(self) -> None:
        super().__init__()
        self.display = ImageDisplay()
        self.width_spinbox = UnitSpinBox("mm", 100)
        self.height_spinbox = UnitSpinBox("mm", 100)

        self.setFrameShape(QFrame.Shape.Panel)
        self.setLayout(self.makeLayout())

    def makeLayout(self) -> QBoxLayout:
        L = QVBoxLayout()
        L.addWidget(self.display)
        L.addLayout(self.funcPanelLayout())
        return L

    def funcPanelLayout(self) -> QBoxLayout:
        L = QHBoxLayout()
        L.addWidget(Button("Нарезать", self.on_button_click))
        L.addStretch()
        L.addWidget(self.width_spinbox)
        L.addWidget(self.height_spinbox)
        return L

    def on_button_click(self) -> None:
        print(f"cut todo, board: {self.width_spinbox.value()}x{self.height_spinbox.value()}")


class LibraryGroup(QGroupBox):

    def __init__(self, tabs: TabWidget) -> None:
        super().__init__("Библиотека")
        self.tabs = tabs
        self.image_file_dialog = FileDialog("Images (*.png *.jpg)")
        self.scroll = VerticalScroll()
        self.setLayout(self.makeLayout())

    def makeLayout(self) -> QBoxLayout:
        L = QVBoxLayout()

        for i in range(1, 50):
            self.scroll.vbox.addWidget(QLabel(f"TextLabel {i}"))

        L.addWidget(self.scroll, 1)
        L.addStretch()
        L.addWidget(Button("Добавить", self.on_button_click))
        return L

    def on_button_click(self) -> None:
        filepath = self.image_file_dialog.get()

        if filepath is None:
            return

        self.tabs.addTabItem(ImageProcessorTab(filepath[0]))


class MainTab(Tab):

    def __init__(self, tabs: TabWidget) -> None:
        super().__init__("Main")
        self.setLayout(self.makeLayout(tabs))

    @staticmethod
    def makeLayout(tabs) -> QBoxLayout:
        L = QHBoxLayout()
        L.addWidget(WorkFieldFrame(), 1)
        L.addWidget(LibraryGroup(tabs))
        return L
