import math
from pathlib import Path

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


class FigureDisplayItem(CollapsingHeader):

    def __init__(self, figure_name: str) -> None:
        super().__init__(figure_name)
        self.__rotate_spinbox = SpinboxInt("rotate", self.redraw, (0, 360), default_value=45, step=15)
        self.__end_angle_spinbox = SpinboxInt("end angle", self.redraw, (0, 360), default_value=270, step=15)

        self.series = LineSeries(figure_name)

        self.position_point = DragPoint(self.__on_position_change, label="Position")

        self.__last_scale = (100, 100)
        self.scale_point = DragPoint(self.__on_scale_change, label="Scale", default_value=self.__last_scale)

    def __on_position_change(self, new_position: tuple[float, float]) -> None:
        scale_x, scale_y = self.__last_scale
        position_x, position_y = new_position

        self.scale_point.setValue((
            position_x + scale_x,
            position_y + scale_y
        ))

        self.redraw()

    def __on_scale_change(self, new_scale: tuple[float, float]) -> None:
        scale_x, scale_y = new_scale
        position_x, position_y = self.getPosition()

        self.__last_scale = (
            scale_x - position_x,
            scale_y - position_y
        )

        self.redraw()

    def getPosition(self) -> tuple[float, float]:
        return self.position_point.getValue()

    def setPosition(self, position: tuple[float, float]) -> None:
        self.position_point.setValue(position)

    def setScale(self, scale: tuple[float, float]) -> None:
        self.__last_scale = scale_x, scale_y = scale
        position_x, position_y = self.getPosition()

        self.scale_point.setValue((
            position_x + scale_x,
            position_y + scale_y
        ))

    def getScale(self) -> tuple[float, float]:
        return self.__last_scale

    def redraw(self, _=None):
        R = range(self.__end_angle_spinbox.getValue() + 1)
        r = self.__rotate_spinbox.getValue()

        scale_x, scale_y = self.getScale()
        position_x, position_y = self.getPosition()

        x = [math.cos(math.radians(i + r)) * scale_x + position_x for i in R]
        y = [math.sin(math.radians(i + r)) * scale_y + position_y for i in R]

        self.series.setValue((x, y))

    def delete(self) -> None:
        super().delete()
        self.series.delete()
        self.position_point.delete()
        self.scale_point.delete()

    def placeRaw(self, parent_id: ItemID) -> None:
        super().placeRaw(parent_id)
        self.add(self.__rotate_spinbox)
        self.add(self.__end_angle_spinbox)
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
        self.canvas.add(circle.position_point).add(circle.scale_point)
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
