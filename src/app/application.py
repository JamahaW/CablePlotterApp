from __future__ import annotations

import math
from pathlib import Path

from dearpygui import dearpygui as dpg

from app.ui.dpg.impl import Button
from app.ui.dpg.impl import FileDialog
from app.ui.dpg.impl import Group
from app.ui.plotter.figure import Canvas
from app.ui.plotter.figure import TransformableFigure
from app.ui.plotter.figure import WorkFieldFigure


class App:

    def __init__(self) -> None:
        self.file_dialog = FileDialog(
            "Select Image file", self.on_image_selected,
            (("png", "Image"),),
            r"A:\Program\Python3\CablePlotterApp\res\images"
        )

        self.work_field = WorkFieldFigure("Work Field")

        self.canvas = Canvas()

        self.items_count = 0

    def addCircleItem(self) -> None:
        R = range(0, 271, 1)
        vertices = (
            [math.cos(math.radians(i)) for i in R],
            [math.sin(math.radians(i)) for i in R]
        )

        circle = TransformableFigure(vertices, f"Figure: Test:{self.items_count}")
        self.items_count += 1

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

        self.canvas.attachFigure(self.work_field)
        self.work_field.setSize((1000, 1000))
        self.work_field.setDeadZone(150, 150, 100, 300)


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
