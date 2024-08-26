from typing import Callable

from app.ui.abc import ItemID
from app.ui.abc import Placeable
from app.ui.abc import VariableItem
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import DragLine
from app.ui.dpg.impl import Group
from app.ui.dpg.impl import SliderInt
from app.ui.dpg.impl import Text


class BorderLinePair(Placeable):

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

    def __init__(self, is_vertical: bool, step) -> None:
        self.__positive_line = DragLine(is_vertical, self.__setHalfSize)
        self.__negative_line = DragLine(is_vertical, self.__setHalfSize)
        self.step = step

    def placeRaw(self, parent_id: ItemID) -> None:
        self.__positive_line.placeRaw(parent_id)
        self.__negative_line.placeRaw(parent_id)

    def __setHalfSize(self, half_size: float) -> None:
        half_size = abs(half_size) // self.step * self.step
        self.__positive_line.setValue(half_size)
        self.__negative_line.setValue(-half_size)

    def setSize(self, size: float) -> None:
        self.__setHalfSize(size / 2)

    def getSize(self) -> float:
        return self.__positive_line.getValue() * 2


class Border(Placeable):

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

    def __init__(self, step: int) -> None:
        self.__width_lines = BorderLinePair(False, step)
        self.__height_lines = BorderLinePair(True, step)

    def placeRaw(self, parent_id: ItemID) -> None:
        self.__width_lines.placeRaw(parent_id)
        self.__height_lines.placeRaw(parent_id)

    def setSize(self, width: int, height: int) -> None:
        self.__width_lines.setSize(width)
        self.__height_lines.setSize(height)

    def getSize(self) -> tuple[float, float]:
        return self.__width_lines.getSize(), self.__height_lines.getSize()


class SpinboxInt(VariableItem[int], Group):

    def __init__(self, label: str, on_change: Callable[[int], None] = None, value_range: tuple[int, int] = (0, 100), *, step: int = 1, default_value: int = 0):
        super().__init__(horizontal=True)
        self.__label = Text(label)
        self.__slider = SliderInt(value_range, None, on_change, default_value=default_value)
        self.__increment_button = Button("[+]", lambda: self.changeValue(step))
        self.__decrement_button = Button("[-]", lambda: self.changeValue(-step))

    def setValue(self, value: int) -> None:
        self.__slider.setValue(value)

    def getValue(self) -> int:
        return self.__slider.getValue()

    def changeValue(self, delta: int) -> None:
        self.setValue(max(min(self.getValue() + delta, self.__slider.getMaxValue()), self.__slider.getMinValue()))

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.addItems((
            self.__label,
            self.__decrement_button,
            self.__slider,
            self.__increment_button,
        ))
