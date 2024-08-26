import math
from pathlib import Path
from typing import Iterable

from dearpygui import dearpygui as dpg

from app.ui.abc import ItemID
from app.ui.custom.widgets import Border
from app.ui.custom.widgets import SpinboxInt
from app.ui.dpg.impl import Axis
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import CollapsingHeader
from app.ui.dpg.impl import DragPoint
from app.ui.dpg.impl import FileDialog
from app.ui.dpg.impl import Group
from app.ui.dpg.impl import LineSeries
from app.ui.dpg.impl import Plot


class FigureSeriesControl(LineSeries):

    def __init__(self, vertices: tuple[Iterable[float], Iterable[float]]) -> None:
        super().__init__()

        self.__angle: int = 0
        self.__scale = (100, 100)

        self.__source_vertices = vertices

        self.position_point = DragPoint(self.__on_position_change, label="Position")
        self.scale_point = DragPoint(self.__on_scale_change, label="Scale", default_value=self.__scale)

    def delete(self) -> None:
        super().delete()
        self.position_point.delete()
        self.scale_point.delete()

    def __on_position_change(self, new_position: tuple[float, float]) -> None:
        scale_x, scale_y = self.__scale
        position_x, position_y = new_position

        self.scale_point.setValue((
            position_x + scale_x,
            position_y + scale_y
        ))

        self.update()

    def __on_scale_change(self, new_scale: tuple[float, float]) -> None:
        scale_x, scale_y = new_scale
        position_x, position_y = self.getPosition()

        self.__scale = (
            scale_x - position_x,
            scale_y - position_y
        )

        self.update()

    def getPosition(self) -> tuple[float, float]:
        return self.position_point.getValue()

    def setPosition(self, position: tuple[float, float]) -> None:
        self.position_point.setValue(position)

    def setRotation(self, angle: int) -> None:
        self.__angle = math.radians(angle)

    def setScale(self, scale: tuple[float, float]) -> None:
        self.__scale = scale_x, scale_y = scale
        position_x, position_y = self.getPosition()

        self.scale_point.setValue((
            position_x + scale_x,
            position_y + scale_y
        ))

    def getScale(self) -> tuple[float, float]:
        return self.__scale

    def __transform_source_vertices(self) -> tuple[list[float], list[float]]:
        transformed_x = list[float]()
        transformed_y = list[float]()

        scale_x, scale_y = self.getScale()
        position_x, position_y = self.getPosition()

        sin_angle = math.sin(self.__angle)
        cos_angle = math.cos(self.__angle)

        source_x, source_y = self.__source_vertices

        for x, y in zip(source_x, source_y):
            # x *= scale_x
            # y *= scale_y

            rx = cos_angle * x - sin_angle * y
            ry = sin_angle * x + cos_angle * y

            # x += position_x
            # y += position_y

            transformed_x.append(rx)
            transformed_y.append(ry)

        return transformed_x, transformed_y

    def update(self) -> None:
        self.setValue(self.__transform_source_vertices())


class FigureDisplayItem(CollapsingHeader):

    def __init__(self, figure_name: str) -> None:
        super().__init__(figure_name)
        self.__rotation_spinbox = SpinboxInt("rotate", self.redraw, (0, 360 * 4), default_value=45, step=15)

        R = range(0, 271, 1)

        self.series = FigureSeriesControl(
            (
                [math.cos(math.radians(i)) for i in R],
                [math.sin(math.radians(i)) for i in R]
            )
        )

    def redraw(self, _=None):
        self.series.setRotation(self.__rotation_spinbox.getValue())
        self.series.update()

    def delete(self) -> None:
        super().delete()
        self.series.delete()

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.__rotation_spinbox)
        self.add(Button("[X]", self.delete))


class Canvas(Plot):

    def __init__(self) -> None:
        super().__init__()
        self.axis = Axis(dpg.mvXAxis)
        self.border = Border(50)

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.axis)
        self.add(self.border)


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.canvas = Canvas()
        self.container_item = Group(width=60)

        self.items_count = 0

    def addCircleItem(self) -> None:
        circle = FigureDisplayItem(f"Circle:{self.items_count}")
        self.items_count += 1
        self.canvas.axis.add(circle.series)
        self.canvas.add(circle.series.position_point).add(circle.series.scale_point)
        self.container_item.add(circle)
        circle.redraw()

    @staticmethod
    def on_image_selected(paths: tuple[Path, ...]) -> None:
        print(paths)

    def build(self) -> None:
        with (dpg.window() as main_window):
            dpg.set_primary_window(main_window, True)

            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    CollapsingHeader("Main").place().add(Button("Open", self.file_dialog.show))
                    CollapsingHeader("Library").place().add(Button("Add", self.addCircleItem)).add(self.container_item)

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
