import math
from pathlib import Path

from dearpygui import dearpygui as dpg

from app_dpg.ui.abc import PlaceableItem
from app_dpg.ui.dpg import Axis
from app_dpg.ui.dpg import Button
from app_dpg.ui.dpg import FileDialog
from app_dpg.ui.dpg import Group
from app_dpg.ui.dpg import Header
from app_dpg.ui.dpg import LineSeries
from app_dpg.ui.dpg import Plot
from app_dpg.ui.dpg import SliderInt
from app_dpg.ui.widgets import Border
from app_dpg.ui.widgets import ItemID


class CircleItem(PlaceableItem):

    def __init__(self, figure_name: str) -> None:
        self.__scale_x = SliderInt((0, 500), "scale x", self.redraw, default_value=200)
        self.__scale_y = SliderInt((0, 500), "scale y", self.redraw, default_value=200)
        self.__offset_x = SliderInt((-500, 500), "offset x", self.redraw)
        self.__offset_y = SliderInt((-500, 500), "offset y", self.redraw)
        self.__rotate = SliderInt((0, 360), "rotate", self.redraw, default_value=45)
        self.__end_angle = SliderInt((0, 360), "end angle", self.redraw, default_value=270)

        self.series = LineSeries(figure_name)
        self.control_panel = Header(figure_name)

    def redraw(self, _=None):
        R = range(self.__end_angle.getValue() + 1)
        r = self.__rotate.getValue()

        x = [math.cos(math.radians(i + r)) * self.__scale_x.getValue() + self.__offset_x.getValue() for i in R]
        y = [math.sin(math.radians(i + r)) * self.__scale_y.getValue() + self.__offset_y.getValue() for i in R]

        self.series.setValue((x, y))

    def placeRaw(self, parent_id: ItemID) -> None:
        self.control_panel.placeRaw(parent_id)
        self.control_panel.add(self.__offset_x)
        self.control_panel.add(self.__offset_y)
        self.control_panel.add(self.__scale_x)
        self.control_panel.add(self.__scale_y)
        self.control_panel.add(self.__rotate)
        self.control_panel.add(self.__end_angle)


class Canvas(PlaceableItem):

    def __init__(self) -> None:
        self.axis = Axis(dpg.mvXAxis)
        self.border = Border(50)
        self.plot = Plot()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.plot.placeRaw(parent_id)
        self.plot.addItems((self.axis, self.border))


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.canvas = Canvas()
        self.test_container_item = Group()

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
        with dpg.window() as main_window:
            dpg.set_primary_window(main_window, True)

            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    Header("Main").place().add(Button("Open", self.file_dialog.show))
                    Header("Library").place().addItems((Button("Add", self.addCircleItem), self.test_container_item))

                self.canvas.place()

        self.canvas.border.setSize(1200, 1200)


if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="title", width=1600, height=900)

    app = App()
    app.build()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # dpg.show_implot_demo()
    # dpg.show_font_manager()
    # dpg.show_style_editor()

    dpg.start_dearpygui()
    dpg.destroy_context()
