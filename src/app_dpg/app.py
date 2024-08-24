import math
from pathlib import Path
from typing import Optional

from dearpygui import dearpygui as dpg

from app_dpg.ui import Axis
from app_dpg.ui import CanvasLines
from app_dpg.ui import FileDialog
from app_dpg.ui import ItemID
from app_dpg.ui import LineSeries


class StackContainer:

    def __init__(self, label: str) -> None:
        self.label = label
        self.items_header: Optional[ItemID] = None
        self.__items_count = 0

    def build(self) -> None:
        with dpg.group():
            dpg.add_button(label="Add", callback=lambda: self.addItem(f"item: {self.__items_count}"))
            self.items_header = dpg.add_collapsing_header(label=self.label)

    def addItem(self, label: str) -> None:
        dpg.add_text(label, parent=self.items_header)
        self.__items_count += 1


class Circle:

    def __init__(self) -> None:
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.rotate = 0
        self.end_angle = 360
        self.series = LineSeries("circle")

    def redraw(self):
        R = range(self.end_angle + 1)

        x = [math.cos(math.radians(i + self.rotate)) * self.scale_x + self.offset_x for i in R]
        y = [math.sin(math.radians(i + self.rotate)) * self.scale_y + self.offset_y for i in R]

        self.series.setValue((x, y))

    def build(self) -> None:
        with dpg.collapsing_header(label="test control", default_open=True):
            dpg.add_slider_int(label="scale_x", max_value=500, callback=self.update_scale_x)
            dpg.add_slider_int(label="scale_y", max_value=500, callback=self.update_scale_y)
            dpg.add_slider_int(label="pos x", max_value=500, callback=self.update_offset_x)
            dpg.add_slider_int(label="pos y", max_value=500, callback=self.update_offset_y)
            dpg.add_slider_int(label="rotate_angle", max_value=360, callback=self.update_rotate_angle)
            dpg.add_slider_int(label="end_angle", max_value=360, callback=self.update_end_angle)

    def update_scale_x(self, __id) -> None:
        self.scale_x = dpg.get_value(__id)
        self.redraw()

    def update_scale_y(self, __id) -> None:
        self.scale_y = dpg.get_value(__id)
        self.redraw()

    def update_rotate_angle(self, __id) -> None:
        self.rotate = dpg.get_value(__id)
        self.redraw()

    def update_end_angle(self, __id) -> None:
        self.end_angle = dpg.get_value(__id)
        self.redraw()

    def update_offset_x(self, __id) -> None:
        self.offset_x = dpg.get_value(__id)
        self.redraw()

    def update_offset_y(self, __id) -> None:
        self.offset_y = dpg.get_value(__id)
        self.redraw()


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
        self.circle_drawer = Circle()
        self.test_stack_container = StackContainer("Test Stack container")

    @staticmethod
    def on_image_selected(paths: tuple[Path, ...]) -> None:
        print(paths)

    def build(self) -> None:
        with dpg.window() as main_window:
            dpg.set_primary_window(main_window, True)

            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    with dpg.collapsing_header(label="Main", default_open=True):
                        dpg.add_button(label="Open", callback=self.file_dialog.show)

                    self.circle_drawer.build()

                    with dpg.collapsing_header(label="test list", default_open=True):
                        self.test_stack_container.build()

                self.plot.build()

        self.circle_drawer.series.build(self.plot.axis)
        self.circle_drawer.redraw()


if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="title", width=1600, height=900)

    app = App()
    app.build()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.show_implot_demo()

    # dpg.show_font_manager()
    # dpg.show_style_editor()

    dpg.start_dearpygui()
    dpg.destroy_context()
