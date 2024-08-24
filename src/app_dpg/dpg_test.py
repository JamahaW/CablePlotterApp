import math
from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Optional

from dearpygui import dearpygui as dpg

CANVAS_HALF_HEIGHT_DEFAULT = 600
CANVAS_HALF_WIDTH_DEFAULT = 600
CANVAS_BORDER_COLOR = (255, 0X74, 0)

type ItemID = int | str


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
        self.items = list[ItemID]()

        with dpg.group():
            self.items_header = dpg.add_collapsing_header(label=label)
            dpg.add_button(
                label="Add item",
                callback=lambda: self.items.append(dpg.add_text(f"item: {len(self.items)}", parent=self.items_header))
            )


def makeFileDialog(label: str, on_select: Callable[[Path], None], extensions: Iterable[tuple[str, str]], default_path: str = "") -> ItemID:
    with dpg.file_dialog(
            label=label,
            callback=lambda _, data: on_select(Path(data["file_path_name"])),
            directory_selector=False,
            show=False,
            width=1200,
            height=800,
            default_path=default_path
    ) as f:
        for extension, text in extensions:
            dpg.add_file_extension(f".{extension}", color=(255, 128, 64, 255), custom_text=f"[{text}]")

        return f


class App:

    def __init__(self) -> None:
        self.circle_drawer = Circle()
        self.test_stack_container: Optional[StackContainer] = None

        self.file_dialog = makeFileDialog("Select Image file", self.on_image_selected, (("png", "Image"),), r"A:\Program\Python3\CablePlotterApp\res\images")

    def on_image_selected(self, path: Path) -> None:
        print(path)

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
                        self.test_stack_container = StackContainer("Items")

                with dpg.plot(height=-1, width=-1, equal_aspects=True):
                    dpg.add_plot_legend()

                    dpg.add_plot_axis(dpg.mvXAxis, label="x")

                    with dpg.plot_axis(dpg.mvYAxis, label="y"):
                        SERIES_TAG = dpg.add_line_series([], [], label="Path")
                        self.circle_drawer.series_tag = SERIES_TAG

                    dpg.add_drag_line(color=CANVAS_BORDER_COLOR, default_value=CANVAS_HALF_WIDTH_DEFAULT)
                    dpg.add_drag_line(color=CANVAS_BORDER_COLOR, default_value=-CANVAS_HALF_WIDTH_DEFAULT)
                    dpg.add_drag_line(color=CANVAS_BORDER_COLOR, vertical=False, default_value=CANVAS_HALF_HEIGHT_DEFAULT)
                    dpg.add_drag_line(color=CANVAS_BORDER_COLOR, vertical=False, default_value=-CANVAS_HALF_HEIGHT_DEFAULT)


if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="title", width=1600, height=900)

    App().build()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
