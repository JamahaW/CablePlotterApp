from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

from dearpygui import dearpygui as dpg

from app.ui.abc import ItemID
from app.ui.custom.widgets import Border
from app.ui.custom.widgets import SpinboxInt
from app.ui.dpg.impl import Axis
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import Checkbox
from app.ui.dpg.impl import DragPoint
from app.ui.dpg.impl import FileDialog
from app.ui.dpg.impl import Group
from app.ui.dpg.impl import LineSeries
from app.ui.dpg.impl import Plot
from app.ui.dpg.impl import Text


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


class FigureSeries(LineSeries):

    def __init__(self, vertices: tuple[Iterable[float], Iterable[float]], label: str) -> None:
        super().__init__(label)
        self.__source_vertices_x, self.__source_vertices_y = vertices
        self.__size = (100, 100)
        self.__sin_angle: float = 0
        self.__cos_angle: float = 0
        self.setRotation(0)

        self.__position_point = DragPoint(self.__onPositionChanged, label="Position")
        self.__size_point = DragPoint(self.__onSizeChanged, label="Size", default_value=self.__size)
        self.__set_controls_visible_checkbox = Checkbox(self.__onSetControlsVisibleChanged, label="Controls Visible", default_value=True)
        self.__status_text = FigureStatusText()

    def getPosition(self) -> tuple[float, float]:
        return self.__position_point.getValue()

    def setRotation(self, angle: int) -> None:
        angle = math.radians(angle)
        self.__sin_angle = math.sin(angle)
        self.__cos_angle = math.cos(angle)

    def setPosition(self, position: tuple[float, float]) -> None:
        self.__position_point.setValue(position)

    def setSize(self, size: tuple[float, float]) -> None:
        position_x, position_y = self.getPosition()
        self.__size = size_x, size_y = size
        self.__size_point.setValue((position_x + size_x, position_y + size_y))

    def getSize(self) -> tuple[float, float]:
        return self.__size

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
        canvas.add(self.__position_point)
        canvas.add(self.__size_point)
        canvas.axis.add(self)
        self.update()

    def update(self) -> None:
        self.setValue(self.getTransformedVertices())

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
        scale_x, scale_y = self.__size
        self.__size_point.setValue((position_x + scale_x, position_y + scale_y))
        self.update()
        self.__status_text.update(new_position, self.__size)

    def __onSizeChanged(self, new_scale: tuple[float, float]) -> None:
        scale_x, scale_y = new_scale
        position_x, position_y = position = self.getPosition()
        self.__size = (scale_x - position_x, scale_y - position_y)
        self.update()
        self.__status_text.update(position, new_scale)

    def __onRotationChanged(self, new_rotation) -> None:
        self.setRotation(new_rotation)
        self.update()

    def __onSetControlsVisibleChanged(self, is_visible: bool) -> None:
        self.__position_point.setVisible(is_visible)
        self.__size_point.setVisible(is_visible)


class Canvas(Plot):

    def __init__(self) -> None:
        super().__init__()
        self.axis = Axis(dpg.mvXAxis)
        self.border = Border(50)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.axis)
        self.add(self.border)

    def attachFigure(self, figure: FigureSeries) -> None:
        figure.attachIntoCanvas(self)


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.canvas = Canvas()

        self.items_count = 0

    def addCircleItem(self) -> None:
        self.items_count += 1

        R = range(0, 271, 1)
        vertices = (
            [math.cos(math.radians(i)) for i in R],
            [math.sin(math.radians(i)) for i in R]
        )

        circle = FigureSeries(vertices, "Figure: Circle-Test")

        self.canvas.attachFigure(circle)

    @staticmethod
    def on_image_selected(paths: tuple[Path, ...]) -> None:
        print(paths)

    def build(self) -> None:
        with (dpg.window() as main_window):
            dpg.set_primary_window(main_window, True)

            with dpg.group():
                Group(horizontal=True).place().add(Button("Open", self.file_dialog.show)).add(Button("Add", self.addCircleItem))

                self.canvas.place()

        self.canvas.border.setSize(1200, 1200)


def start_application(app_title: str, window_width: int, window_height: int) -> None:
    dpg.create_context()
    dpg.create_viewport(title=app_title, width=window_width, height=window_height)
    app = App()
    app.build()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.show_implot_demo()
    # dpg.show_font_manager()
    # dpg.show_style_editor()
    dpg.start_dearpygui()
    dpg.destroy_context()
