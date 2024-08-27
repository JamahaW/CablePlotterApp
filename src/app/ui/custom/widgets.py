from typing import Callable

from app.ui.abc import ItemID
from app.ui.abc import Placeable
from app.ui.abc import RangedItem
from app.ui.abc import VariableItem
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import DragLine
from app.ui.dpg.impl import Group
from app.ui.dpg.impl import SliderInt
from app.ui.dpg.impl import Text


class BorderLinePair(Placeable, VariableItem[float]):

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None, *, step: int = 1) -> None:
        self.__positive_line = DragLine(is_vertical, self.__setHalfSize)
        self.__negative_line = DragLine(is_vertical, self.__setHalfSize)
        self.__on_change = on_change
        self.step = step

    def setValue(self, size: float) -> None:
        self.__on_change(size)
        self.__setHalfSize(size / 2)

    def getValue(self) -> float:
        return self.__positive_line.getValue() * 2

    def hide(self) -> None:
        self.__positive_line.hide()
        self.__negative_line.hide()

    def getItemID(self) -> ItemID:
        pass

    def enable(self) -> None:
        self.__positive_line.enable()
        self.__negative_line.enable()

    def disable(self) -> None:
        self.__positive_line.disable()
        self.__negative_line.disable()

    def delete(self) -> None:
        self.__positive_line.delete()
        self.__negative_line.delete()

    def show(self) -> None:
        self.__positive_line.show()
        self.__negative_line.show()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.__positive_line.placeRaw(parent_id)
        self.__negative_line.placeRaw(parent_id)

    def __setHalfSize(self, half_size: float) -> None:
        half_size = abs(half_size) // self.step * self.step
        self.__positive_line.setValue(half_size)
        self.__negative_line.setValue(-half_size)

        if self.__on_change:
            self.__on_change(half_size * 2)


class Border(Placeable, VariableItem[tuple[float, float]]):

    def __init__(self, on_change: Callable[[tuple[float, float]], None] = None, *, step: int) -> None:
        on_width_changed = None if on_change is None else lambda width: on_change((width, self.__height_lines.getValue()))
        on_height_changed = None if on_change is None else lambda height: on_change((self.__width_lines.getValue(), height))
        self.__on_change = on_change
        self.__width_lines = BorderLinePair(True, on_width_changed, step=step)
        self.__height_lines = BorderLinePair(False, on_height_changed, step=step)

    def setValue(self, size: tuple[float, float]) -> None:
        width, height = size
        self.__width_lines.setValue(width)
        self.__height_lines.setValue(height)

        if self.__on_change:
            self.__on_change(size)

    def getValue(self) -> tuple[float, float]:
        return self.__width_lines.getValue(), self.__height_lines.getValue()

    def show(self) -> None:
        self.__width_lines.show()
        self.__height_lines.show()

    def hide(self) -> None:
        self.__width_lines.hide()
        self.__height_lines.hide()

    def getItemID(self) -> ItemID:
        pass

    def disable(self) -> None:
        self.__width_lines.disable()
        self.__height_lines.disable()

    def enable(self) -> None:
        self.__width_lines.enable()
        self.__height_lines.enable()

    def delete(self) -> None:
        self.__width_lines.delete()
        self.__height_lines.delete()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.__width_lines.placeRaw(parent_id)
        self.__height_lines.placeRaw(parent_id)


class SpinboxInt(Group, RangedItem[int]):

    def __init__(self, label: str, on_change: Callable[[int], None] = None, *, value_range: tuple[int, int] = (0, 100), step: int = 1, default_value: int = 0):
        super().__init__(horizontal=True)
        self.__label = Text(label)
        self.__slider = SliderInt(value_range, None, on_change, default_value=default_value)
        self.__increment_button = Button("[+]", lambda: self.changeValue(step))
        self.__decrement_button = Button("[-]", lambda: self.changeValue(-step))
        self.__on_change = on_change

    def setMaxValue(self, value: int) -> None:
        self.__slider.setMaxValue(value)

    def setMinValue(self, value: int) -> None:
        self.__slider.setMinValue(value)

    def getMinValue(self) -> int:
        return self.__slider.getMinValue()

    def getMaxValue(self) -> int:
        return self.__slider.getMaxValue()

    def setValue(self, value: int) -> None:
        self.__slider.setValue(value)

    def getValue(self) -> int:
        return self.__slider.getValue()

    def changeValue(self, delta: int) -> None:
        value = max(min(self.getValue() + delta, self.__slider.getMaxValue()), self.__slider.getMinValue())
        self.setValue(value)

        if self.__on_change is not None:
            self.__on_change(value)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.__decrement_button).add(self.__slider).add(self.__increment_button).add(self.__label)
