from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QBoxLayout
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class VerticalScroll(QScrollArea):

    def __init__(self) -> None:
        super().__init__()
        self.vbox = QVBoxLayout()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.makeLayoutWidget(self.vbox))

    @staticmethod
    def makeLayoutWidget(layout: QBoxLayout) -> QWidget:
        W = QWidget()
        W.setLayout(layout)
        return W

    def addWidget(self, widget: QWidget) -> None:
        self.vbox.addWidget(widget)
