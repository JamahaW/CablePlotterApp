from __future__ import annotations

import math
from abc import ABC
from abc import abstractmethod
from typing import Final
from typing import Iterable

from dearpygui import dearpygui as dpg

from app.ui.abc import ItemID
from app.ui.custom.widgets import Border
from app.ui.custom.widgets import SpinboxInt
from app.ui.dpg.impl import Axis
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import Checkbox
from app.ui.dpg.impl import CollapsingHeader
from app.ui.dpg.impl import DragPoint
from app.ui.dpg.impl import LineSeries
from app.ui.dpg.impl import Plot
from app.ui.dpg.impl import Text


class Figure(LineSeries, ABC):

    def __init__(self, vertices: tuple[Iterable[float], Iterable[float]], label: str, size: tuple[int, int] = (0, 0)) -> None:
        super().__init__(label)
        source_x, source_y = vertices
        self.source_vertices_x: Final[Iterable[float]] = source_x
        self.source_vertices_y: Final[Iterable[float]] = source_y
        self.__size = size

    @abstractmethod
    def getTransformedVertices(self) -> tuple[list[float], list[float]]:
        pass

    @abstractmethod
    def attachIntoCanvas(self, canvas: Canvas) -> None:
        pass

    def getSize(self) -> tuple[float, float]:
        return self.__size

    def setSize(self, size: tuple[float, float]) -> None:
        self.__size = size

    def update(self) -> None:
        self.setValue(self.getTransformedVertices())


class Canvas(Plot):

    def __init__(self) -> None:
        super().__init__()
        self.axis = Axis(dpg.mvXAxis)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.axis)

    def attachFigure(self, figure: Figure) -> None:
        figure.attachIntoCanvas(self)


class WorkAreaFigure(Figure):
    __WORK_AREA_VERTICES: Final[tuple[Iterable[float], Iterable[float]]] = (
        (0.5, 0.5, -0.5, -0.5, 0.5),
        (0.5, -0.5, -0.5, 0.5, 0.5)
    )

    def __init__(self, label: str):
        super().__init__(self.__WORK_AREA_VERTICES, label)
        self.__border = Border(self.__onSizeChanged, step=50)

        self.__left_dead_zone_spinbox = SpinboxInt("Left", (0, 500), self.__onLeftDeadZoneChanged, step=10)
        self.__right_dead_zone_spinbox = SpinboxInt("Right", (0, 500), self.__onRightDeadZoneChanged, step=10)
        self.__bottom_dead_zone_spinbox = SpinboxInt("Bottom", (0, 500), self.__onBottomDeadZoneChanged, step=10)
        self.__top_dead_zone_spinbox = SpinboxInt("Top", (0, 500), self.__onTopDeadZoneChanged, step=10)

    def getBottomDeadZone(self) -> int:
        return self.__bottom_dead_zone_spinbox.getValue()

    def getTopDeadZone(self) -> int:
        return self.__top_dead_zone_spinbox.getValue()

    def getLeftDeadZone(self) -> int:
        return self.__left_dead_zone_spinbox.getValue()

    def getRightDeadZone(self) -> int:
        return self.__right_dead_zone_spinbox.getValue()

    def setDeadZone(self, left: int, right: int, top: int, bottom: int) -> None:
        self.__left_dead_zone_spinbox.setValue(left)
        self.__right_dead_zone_spinbox.setValue(right)
        self.__top_dead_zone_spinbox.setValue(top)
        self.__bottom_dead_zone_spinbox.setValue(bottom)

    def setSize(self, size: tuple[float, float]) -> None:
        super().setSize(size)
        self.__border.setValue(size)

    def attachIntoCanvas(self, canvas: Canvas) -> None:
        canvas.axis.add(self)
        canvas.add(self.__border)

    def getTransformedVertices(self) -> tuple[list[float], list[float]]:
        size_x, size_y = self.getSize()

        left_dead_zone = self.getLeftDeadZone()
        right_dead_zone = self.getRightDeadZone()
        top_dead_zone = self.getTopDeadZone()
        bottom_dead_zone = self.getBottomDeadZone()

        area_width = size_x - left_dead_zone - right_dead_zone
        area_height = size_y - top_dead_zone - bottom_dead_zone

        offset_x = (left_dead_zone - right_dead_zone) / 2
        offset_y = (bottom_dead_zone - top_dead_zone) / 2

        return (
            [x * area_width + offset_x for x in self.source_vertices_x],
            [y * area_height + offset_y for y in self.source_vertices_y],
        )

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)

        dead_zone_header = CollapsingHeader("DeadZone")
        self.add(dead_zone_header)
        dead_zone_header.add(self.__left_dead_zone_spinbox).add(self.__right_dead_zone_spinbox).add(self.__top_dead_zone_spinbox).add(self.__bottom_dead_zone_spinbox)

    def __onSizeChanged(self, new_size: tuple[float, float]) -> None:
        super().setSize(new_size)
        self.update()

    def __onLeftDeadZoneChanged(self, _) -> None:
        self.update()

    def __onRightDeadZoneChanged(self, _) -> None:
        self.update()

    def __onBottomDeadZoneChanged(self, _) -> None:
        self.update()

    def __onTopDeadZoneChanged(self, _) -> None:
        self.update()


class FigureStatusText(Text):

    @staticmethod
    def __getString(position: tuple[float, float], size: tuple[float, float]) -> str:
        px, py = position
        sx, sy = size
        return f"Position: {px:.1f}x{py:.1f}, Size: {sx:.1f}x{sy:.1f}"

    def update(self, position: tuple[float, float], size: tuple[float, float]) -> None:
        self.setValue(self.__getString(position, size))

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.update((0, 0), (0, 0))


class TransformableFigure(Figure):

    def __init__(self, vertices: tuple[Iterable[float], Iterable[float]], label: str) -> None:
        super().__init__(vertices, label, (100, 100))
        self.__source_vertices_x, self.__source_vertices_y = vertices

        self.__sin_angle: float = 0
        self.__cos_angle: float = 0
        self.setRotation(0)

        self.__position_point = DragPoint(self.__onPositionChanged, label="Position")
        self.__size_point = DragPoint(self.__onSizeChanged, label="Size", default_value=self.getSize())
        self.__set_controls_visible_checkbox = Checkbox(self.__onSetControlsVisibleChanged, label="Controls Visible", default_value=True)
        self.__status_text = FigureStatusText()

    def setRotation(self, angle: int) -> None:
        angle = math.radians(angle)
        self.__sin_angle = math.sin(angle)
        self.__cos_angle = math.cos(angle)

    def getPosition(self) -> tuple[float, float]:
        return self.__position_point.getValue()

    def setPosition(self, position: tuple[float, float]) -> None:
        self.__position_point.setValue(position)

    def setSize(self, size: tuple[float, float]) -> None:
        super().setSize(size)
        size_x, size_y = size
        position_x, position_y = self.getPosition()
        self.__size_point.setValue((position_x + size_x, position_y + size_y))

    def getTransformedVertices(self) -> tuple[list[float], list[float]]:
        transformed_x = list[float]()
        transformed_y = list[float]()

        size_x, size_y = self.getSize()
        position_x, position_y = self.getPosition()

        sin_angle = self.__sin_angle
        cos_angle = self.__cos_angle

        for x, y in zip(self.__source_vertices_x, self.__source_vertices_y):
            x *= size_x
            y *= size_y

            transformed_x.append(cos_angle * x - sin_angle * y + position_x)
            transformed_y.append(sin_angle * x + cos_angle * y + position_y)

        return transformed_x, transformed_y

    def attachIntoCanvas(self, canvas: Canvas) -> None:
        canvas.axis.add(self)
        canvas.add(self.__position_point)
        canvas.add(self.__size_point)
        self.update()

    def delete(self) -> None:
        super().delete()
        self.__position_point.delete()
        self.__size_point.delete()

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.__status_text)
        self.add(SpinboxInt("rotation", (0, 360), self.__onRotationChanged, step=15, default_value=0))
        self.add(self.__set_controls_visible_checkbox)
        self.add(Button("[Remove]", self.delete))

    def __onPositionChanged(self, new_position: tuple[float, float]) -> None:
        position_x, position_y = new_position
        scale_x, scale_y = self.getSize()
        self.__size_point.setValue((position_x + scale_x, position_y + scale_y))
        self.update()
        self.__status_text.update(new_position, self.getSize())

    def __onSizeChanged(self, new_scale: tuple[float, float]) -> None:
        scale_x, scale_y = new_scale
        position_x, position_y = position = self.getPosition()
        self.setSize((scale_x - position_x, scale_y - position_y))
        self.update()
        self.__status_text.update(position, new_scale)

    def __onRotationChanged(self, new_rotation) -> None:
        self.setRotation(new_rotation)
        self.update()

    def __onSetControlsVisibleChanged(self, is_visible: bool) -> None:
        self.__position_point.setVisible(is_visible)
        self.__size_point.setVisible(is_visible)
