from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Optional

from dearpygui import dearpygui as dpg

type ItemID = int | str


class DPGItem:

    def __init__(self) -> None:
        self.dpg_item_id: Optional[ItemID] = None

    def getItemID(self) -> ItemID:
        return self.dpg_item_id

    def configure(self, **kwargs) -> None:
        dpg.configure_item(self.dpg_item_id, **kwargs)

    def hide(self) -> None:
        dpg.hide_item(self.dpg_item_id)

    def show(self) -> None:
        dpg.show_item(self.dpg_item_id)

    def enable(self) -> None:
        dpg.enable_item(self.dpg_item_id)

    def disable(self) -> None:
        dpg.disable_item(self.dpg_item_id)

    def delete(self) -> None:
        dpg.delete_item(self.dpg_item_id)


class PlaceableItem(ABC):

    def place(self, parent: DPGItem = None) -> PlaceableItem:
        self.placeRaw(0 if parent is None else parent.getItemID())
        return self

    @abstractmethod
    def placeRaw(self, parent_id: ItemID) -> None:
        pass


class ContainerDPGItem(PlaceableItem, DPGItem, ABC):

    def add(self, item: PlaceableItem) -> ContainerDPGItem:
        item.place(self)
        return self

    def addItems(self, items: Iterable[PlaceableItem]) -> ContainerDPGItem:
        for item in items:
            self.add(item)

        return self


class VariableItem[T](ABC):

    @abstractmethod
    def setValue(self, value: T) -> None:
        pass

    @abstractmethod
    def getValue(self) -> T:
        pass


class VariableDPGItem[T](DPGItem, VariableItem):
    def setValue(self, value: T) -> None:
        dpg.set_value(self.dpg_item_id, value)

    def getValue(self) -> T:
        return dpg.get_value(self.dpg_item_id)
