from app_dpg.ui.abc import ItemID
from app_dpg.ui.abc import PlaceableItem
from app_dpg.ui.dpg import DragLine


class BorderLinePair(PlaceableItem):

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


class Border(PlaceableItem):

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
