import math
from pathlib import Path

from dearpygui import dearpygui as dpg

from app_dpg.ui import Axis
from app_dpg.ui import Button
from app_dpg.ui import CanvasLines
from app_dpg.ui import FileDialog
from app_dpg.ui import Group
from app_dpg.ui import Header
from app_dpg.ui import ItemID
from app_dpg.ui import LineSeries
from app_dpg.ui import PlaceableItem
from app_dpg.ui import SliderInt


class CircleItem(PlaceableItem):

    def __init__(self) -> None:
        self.__scale_x = SliderInt((0, 500), "scale x", self.redraw, default_value=200)
        self.__scale_y = SliderInt((0, 500), "scale y", self.redraw, default_value=200)
        self.__offset_x = SliderInt((-500, 500), "offset x", self.redraw)
        self.__offset_y = SliderInt((-500, 500), "offset y", self.redraw)
        self.__rotate = SliderInt((0, 360), "rotate", self.redraw, default_value=45)
        self.__end_angle = SliderInt((0, 360), "end angle", self.redraw, default_value=270)

        self.series = LineSeries("circle")

    def redraw(self, _=None):
        R = range(self.__end_angle.getValue() + 1)
        r = self.__rotate.getValue()

        x = [math.cos(math.radians(i + r)) * self.__scale_x.getValue() + self.__offset_x.getValue() for i in R]
        y = [math.sin(math.radians(i + r)) * self.__scale_y.getValue() + self.__offset_y.getValue() for i in R]

        self.series.setValue((x, y))

    def placeRaw(self, parent_id: ItemID) -> None:
        control = Header("Control")
        control.placeRaw(parent_id)
        control.add(self.__offset_x)
        control.add(self.__offset_y)
        control.add(self.__scale_x)
        control.add(self.__scale_y)
        control.add(self.__rotate)
        control.add(self.__end_angle)


class Plot:

    def __init__(self) -> None:
        self.canvas_border = CanvasLines(50)
        self.axis = Axis(dpg.mvXAxis)

    def build(self) -> None:
        with dpg.plot(height=-1, width=-1, equal_aspects=True):
            dpg.add_plot_legend()
            self.axis.build()
            self.canvas_border.build()


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.plot = Plot()
        self.circle_drawer = CircleItem()

        self.test_container_item = Group()

    def addCircleItem(self) -> None:
        circle = CircleItem()
        circle.series.build(self.plot.axis)
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

                    Header("Library").place().addItems((
                        Button("Add", self.addCircleItem),
                        self.test_container_item
                    ))

                self.plot.build()

        self.plot.canvas_border.setSize(1200, 1200)


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
