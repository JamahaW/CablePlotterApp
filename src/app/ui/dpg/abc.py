from __future__ import annotations

from abc import ABC
from typing import Callable
from typing import Optional

from dearpygui import dearpygui as dpg

from app.ui.abc import Item
from app.ui.abc import ItemID
from app.ui.abc import Placeable
from app.ui.abc import VariableItem


class DPGItem(Item):
    __dpg_item_id: Optional[ItemID]

    def __init__(self) -> None:
        self.__dpg_item_id = None

    def getItemID(self) -> ItemID:
        return self.__dpg_item_id

    def setItemID(self, item_id: ItemID) -> None:
        if self.__dpg_item_id is not None:
            raise ValueError("setItemID must called once")

        self.__dpg_item_id = item_id

    def hide(self) -> None:
        dpg.hide_item(self.__dpg_item_id)

    def show(self) -> None:
        dpg.show_item(self.__dpg_item_id)

    def enable(self) -> None:
        dpg.enable_item(self.__dpg_item_id)

    def disable(self) -> None:
        dpg.disable_item(self.__dpg_item_id)

    def delete(self) -> None:
        dpg.delete_item(self.__dpg_item_id)

    def configure(self, **kwargs) -> None:
        dpg.configure_item(self.__dpg_item_id, **kwargs)


class VariableDPGItem[T](DPGItem, VariableItem[T]):
    def setValue(self, value: T) -> None:
        dpg.set_value(self.getItemID(), value)

    def getValue(self) -> T:
        return dpg.get_value(self.getItemID())


class Slider[T: (float, int)](VariableDPGItem[T], Placeable, ABC):

    def __init__(
            self,
            value_range: tuple[T, T],
            label: str = None,
            on_change: Callable[[T], None] = None,
            *,
            default_value: T = 0
    ):
        super().__init__()
        self._callback = None if on_change is None else lambda: on_change(self.getValue())
        self._label = label
        self._default_value = default_value
        self._min_value, self._max_value = value_range

    def getMaxValue(self) -> T:
        return self._max_value

    def getMinValue(self) -> T:
        return self._min_value
