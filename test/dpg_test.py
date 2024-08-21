import math

import dearpygui.dearpygui as dpg

PRIMARY_WINDOW_TAG = "primary::window"

CANVAS_HALF_HEIGHT_DEFAULT = 600
CANVAS_HALF_WIDTH_DEFAULT = 600
CANVAS_BORDER_COLOR = (255, 0X74, 0)
SERIES_TAG = "SERIES_TAG"


class GraphDrawer:

    def __init__(self) -> None:
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.rotate = 0
        self.end_angle = 360

    def redraw(self):
        R = range(0, self.end_angle + 1, 1)

        x = [math.cos(math.radians(i + self.rotate)) * self.scale_x for i in R]
        y = [math.sin(math.radians(i + self.rotate)) * self.scale_y for i in R]
        dpg.set_value(SERIES_TAG, (x, y))

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


def main():
    drawer = GraphDrawer()

    dpg.create_context()
    dpg.setup_dearpygui()

    with dpg.window() as main_window:
        dpg.set_primary_window(main_window, True)

        with dpg.group(horizontal=True):
            with dpg.group(label="Config"):
                with dpg.collapsing_header(label="circle"):
                    dpg.add_slider_int(label="scale_x", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=drawer.update_scale_x, width=200)
                    dpg.add_slider_int(label="scale_y", max_value=CANVAS_HALF_WIDTH_DEFAULT, callback=drawer.update_scale_y, width=200)
                    dpg.add_slider_int(label="rotate_angle", max_value=360, callback=drawer.update_rotate_angle, width=200)
                    dpg.add_slider_int(label="end_angle", max_value=360, callback=drawer.update_end_angle, width=200)

            with dpg.plot(label="Move Display", height=-1, width=-1, equal_aspects=True):
                dpg.add_plot_legend()

                dpg.add_plot_axis(dpg.mvXAxis, label="x")
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y")

                dpg.add_line_series([], [], label="Path", tag=SERIES_TAG, parent=y_axis)

                dpg.add_drag_line(color=CANVAS_BORDER_COLOR, default_value=CANVAS_HALF_WIDTH_DEFAULT)
                dpg.add_drag_line(color=CANVAS_BORDER_COLOR, default_value=-CANVAS_HALF_WIDTH_DEFAULT)
                dpg.add_drag_line(color=CANVAS_BORDER_COLOR, vertical=False, default_value=CANVAS_HALF_HEIGHT_DEFAULT)
                dpg.add_drag_line(color=CANVAS_BORDER_COLOR, vertical=False, default_value=-CANVAS_HALF_HEIGHT_DEFAULT)

    dpg.create_viewport(title="Cable plotter app (dearpygui)", width=1600, height=900)
    dpg.show_viewport()

    dpg.start_dearpygui()
    dpg.destroy_context()

    return


if __name__ == '__main__':
    main()
