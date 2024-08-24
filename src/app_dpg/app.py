import math
from pathlib import Path
from typing import Optional

from dearpygui import dearpygui as dpg

from app_dpg.ui import DragLine
from app_dpg.ui import ItemID
from app_dpg.ui import makeFileDialog

CANVAS_HALF_HEIGHT_DEFAULT = 600
CANVAS_HALF_WIDTH_DEFAULT = 600


class Circle:

    def __init__(self) -> None:
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.offset_x = 0
        self.offset_y = 0
        self.rotate = 0
        self.end_angle = 360
        self.series_tag: Optional[ItemID] = None

    def redraw(self):
        R = range(self.end_angle + 1)

        x = [math.cos(math.radians(i + self.rotate)) * self.scale_x + self.offset_x for i in R]
        y = [math.sin(math.radians(i + self.rotate)) * self.scale_y + self.offset_y for i in R]
        dpg.set_value(self.series_tag, (x, y))

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


class CanvasPlot:
    CANVAS_BORDER_COLOR = (255, 0X74, 0)

    def __init__(self, width: int, height: int) -> None:
        self.half_width = width // 2
        self.half_height = height // 2

        # items

        self.x_axis: Optional[ItemID] = None
        self.y_axis: Optional[ItemID] = None

        self.canvas_half_width_positive = DragLine(False, self.half_width, color=self.CANVAS_BORDER_COLOR)
        self.canvas_half_width_negative = DragLine(False, -self.half_width, color=self.CANVAS_BORDER_COLOR)
        self.canvas_half_height_positive = DragLine(True, self.half_height, color=self.CANVAS_BORDER_COLOR)
        self.canvas_half_height_negative = DragLine(True, -self.half_height, color=self.CANVAS_BORDER_COLOR)

    def build(self) -> None:
        with dpg.plot(height=-1, width=-1, equal_aspects=True):
            dpg.add_plot_legend()

            self.x_axis = dpg.add_plot_axis(dpg.mvXAxis)
            self.y_axis = dpg.add_plot_axis(dpg.mvYAxis)

            self.canvas_half_width_positive.build()
            self.canvas_half_width_negative.build()
            self.canvas_half_height_positive.build()
            self.canvas_half_height_negative.build()

    def addSeries(self, label: str) -> ItemID:
        return dpg.add_line_series(tuple(), tuple(), label=label, parent=self.y_axis)


class App:

    def __init__(self) -> None:
        self.circle_drawer = Circle()
        self.test_stack_container = StackContainer("Test Stack container")

        self.file_dialog = makeFileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.plot = CanvasPlot(1200, 1200)

    def on_image_selected(self, paths: tuple[Path, ...]) -> None:
        print(paths)

    def build(self) -> None:
        with dpg.window() as main_window:
            dpg.set_primary_window(main_window, True)

            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    with dpg.collapsing_header(label="Main"):
                        dpg.add_button(label="Open", callback=lambda: dpg.show_item(self.file_dialog))

                    with dpg.collapsing_header(label="test control"):
                        dpg.add_slider_int(label="scale_x", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=self.circle_drawer.update_scale_x)
                        dpg.add_slider_int(label="scale_y", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=self.circle_drawer.update_scale_y)
                        dpg.add_slider_int(label="pos x", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=self.circle_drawer.update_offset_x)
                        dpg.add_slider_int(label="pos y", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=self.circle_drawer.update_offset_y)
                        dpg.add_slider_int(label="rotate_angle", max_value=360, callback=self.circle_drawer.update_rotate_angle)
                        dpg.add_slider_int(label="end_angle", max_value=360, callback=self.circle_drawer.update_end_angle)

                    with dpg.collapsing_header(label="test list"):
                        self.test_stack_container.build()

                self.plot.build()

        self.circle_drawer.series_tag = self.plot.addSeries("path")


if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="title", width=1600, height=900)

    App().build()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # dpg.show_style_editor()

    dpg.start_dearpygui()
    dpg.destroy_context()
