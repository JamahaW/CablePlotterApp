from __future__ import annotations

from typing import Optional

from dearpygui import dearpygui as dpg

from app.ui.abc import Item
from app.ui.abc import ItemID
from app.ui.abc import RangedItem
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

    def setConfiguration(self, **kwargs) -> None:
        dpg.configure_item(self.__dpg_item_id, **kwargs)

    def getConfiguration(self) -> dict[str, float | int | bool | str]:
        return dpg.get_item_configuration(self.__dpg_item_id)


class VariableDPGItem[T](DPGItem, VariableItem[T]):
    def setValue(self, value: T) -> None:
        dpg.set_value(self.getItemID(), value)

    def getValue(self) -> T:
        return dpg.get_value(self.getItemID())


class RangedDPGItem[T](RangedItem, VariableDPGItem):

    def getMinValue(self) -> T:
        return self.getConfiguration().get("min_value")

    def getMaxValue(self) -> T:
        return self.getConfiguration().get("max_value")

    def setMinValue(self, value: T) -> None:
        self.setConfiguration(min_value=value)
        super().setMinValue(value)

    def setMaxValue(self, value: T) -> None:
        self.setConfiguration(max_value=value)
        super().setMaxValue(value)
