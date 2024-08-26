import math
from pathlib import Path

from dearpygui import dearpygui as dpg

from app.ui.custom.widgets import Border
from app.ui.custom.widgets import ItemID
from app.ui.custom.widgets import SpinboxInt
from app.ui.dpg.impl import Axis
from app.ui.dpg.impl import Button
from app.ui.dpg.impl import CollapsingHeader
from app.ui.dpg.impl import DragPoint
from app.ui.dpg.impl import FileDialog
from app.ui.dpg.impl import Group
from app.ui.dpg.impl import LineSeries
from app.ui.dpg.impl import Plot
from app.ui.dpg.impl import SliderInt


class CircleItem(CollapsingHeader):

    def __init__(self, figure_name: str) -> None:
        super().__init__(figure_name)
        self.__scale_x = SliderInt((0, 500), "scale x", self.redraw, default_value=200)
        self.__scale_y = SliderInt((0, 500), "scale y", self.redraw, default_value=200)

        self.__offset_x = SliderInt((-500, 500), "offset x", self.redraw)
        self.__offset_y = SliderInt((-500, 500), "offset y", self.redraw)

        self.__rotate = SpinboxInt("rotate", self.redraw, (0, 360), default_value=45, step=15)
        self.__end_angle = SpinboxInt("end angle", self.redraw, (0, 360), default_value=270, step=15)

        self.series = LineSeries(figure_name)

    def redraw(self, _=None):
        R = range(self.__end_angle.getValue() + 1)
        r = self.__rotate.getValue()

        x = [math.cos(math.radians(i + r)) * self.__scale_x.getValue() + self.__offset_x.getValue() for i in R]
        y = [math.sin(math.radians(i + r)) * self.__scale_y.getValue() + self.__offset_y.getValue() for i in R]

        self.series.setValue((x, y))

    def delete(self) -> None:
        super().delete()
        self.series.delete()

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)

        pos = Group(horizontal=True)
        self.add(pos)
        pos.add(self.__offset_x)
        pos.add(self.__offset_y)

        scale = Group(horizontal=True)
        self.add(scale)
        scale.add(self.__scale_x)
        scale.add(self.__scale_y)

        self.add(self.__rotate)
        self.add(self.__end_angle)
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
        self.add(DragPoint())


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.canvas = Canvas()
        self.test_container_item = Group(width=60)

        self.items_count = 0

    def addCircleItem(self) -> None:
        circle = CircleItem(f"Circle:{self.items_count}")
        self.items_count += 1
        circle.series.place(self.canvas.axis)
        self.test_container_item.add(circle)
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
                    CollapsingHeader("Library").place().add(Button("Add", self.addCircleItem)).add(self.test_container_item)

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
