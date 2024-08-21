from __future__ import annotations

from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QWidget


class Tab(QWidget):

    def __init__(self, title: str, closeable: bool = False) -> None:
        super().__init__()
        self.title = title
        self.closeable = closeable


class TabWidget(QTabWidget):

    def __init__(self, movable: bool = False, closeable: bool = False) -> None:
        super().__init__()
        self.setMovable(movable)
        self.setTabsClosable(closeable)
        self.__closeable_items_indices = set[int]()

        if closeable:
            # noinspection PyUnresolvedReferences
            self.tabCloseRequested.connect(self.__onTabCloseRequest)

    def addTabItem(self, tab: Tab) -> TabWidget:
        if tab.closeable:
            self.__closeable_items_indices.add(self.count())

        self.addTab(tab, tab.title)
        return self

    def __onTabCloseRequest(self, index: int) -> None:
        if index not in self.__closeable_items_indices:
            return

        self.removeTab(index)
