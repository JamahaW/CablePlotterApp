import sys

import qdarktheme
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow

from cableplotter_qt.app.tabs.main import MainTab
from cableplotter_qt.app.tabs.test import TestTab
from cableplotter_qt.ui.tab import TabWidget


class App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        qdarktheme.setup_theme()
        self.main_window = MainWindow()
        self.main_window.show()


class MainWidget(TabWidget):

    def __init__(self):
        super().__init__(True, True)
        self.addTabItem(MainTab(self))
        self.addTabItem(TestTab())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест PyQT + OpenCV + Numpy")
        self.setMinimumSize(800, 450)

        self.setCentralWidget(MainWidget())
