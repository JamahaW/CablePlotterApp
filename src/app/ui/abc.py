from __future__ import annotations

from abc import ABC
from abc import abstractmethod

type ItemID = int | str


class Item(ABC):

    @abstractmethod
    def getItemID(self) -> ItemID:
        pass

    @abstractmethod
    def enable(self) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def hide(self) -> None:
        pass

    def setVisible(self, is_visible: bool) -> None:
        if is_visible:
            self.show()
        else:
            self.hide()


class Placeable(Item):

    def place(self, parent: Item = None) -> Placeable:
        self.placeRaw(0 if parent is None else parent.getItemID())
        return self

    @abstractmethod
    def placeRaw(self, parent_id: ItemID) -> None:
        pass


class Container(Item, ABC):

    def add(self, item: Placeable) -> Container:
        item.place(self)
        return self


class VariableItem[T](ABC):

    @abstractmethod
    def setValue(self, value: T) -> None:
        pass

    @abstractmethod
    def getValue(self) -> T:
        pass