from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import Iterable

from dearpygui import dearpygui as dpg

from app.ui.abc import Color3i
from app.ui.abc import Container
from app.ui.abc import ItemID
from app.ui.abc import Placeable
from app.ui.dpg.abc import DPGItem
from app.ui.dpg.abc import Slider
from app.ui.dpg.abc import VariableDPGItem


class Group(DPGItem, Container, Placeable):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__kwargs = kwargs

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_group(
            parent=parent_id,
            **self.__kwargs
        ))

    def _cleanup(self) -> None:
        del self.__kwargs


class CollapsingHeader(Container, DPGItem, Placeable):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_collapsing_header(label=self.__label, parent=parent_id))

    def _cleanup(self) -> None:
        del self.__label


class Plot(Container, DPGItem, Placeable):

    def placeRaw(self, parent_id: ItemID) -> None:
        with dpg.plot(width=-1, height=-1, equal_aspects=True, anti_aliased=True, parent=parent_id) as plot:
            self.setItemID(plot)
            dpg.add_plot_legend(horizontal=True)


class Text(VariableDPGItem[str], Placeable):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        dpg.add_text(self.__label, parent=parent_id)

    def _cleanup(self) -> None:
        del self.__label


class SliderInt(Slider[int]):

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_slider_int(
            label=self._label,
            callback=self._callback,
            min_value=self.getMinValue(),
            max_value=self.getMaxValue(),
            parent=parent_id,
            default_value=self._default_value,
        ))


class SliderFloat(Slider[float]):

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_slider_double(
            label=self._label,
            callback=self._callback,
            min_value=self.getMinValue(),
            max_value=self.getMaxValue(),
            parent=parent_id,
            default_value=self._default_value
        ))


class Button(DPGItem, Placeable):

    def __init__(self, label: str, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.__label = label
        self.__callback = lambda: on_click()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_button(label=self.__label, callback=self.__callback, parent=parent_id))

    def _cleanup(self) -> None:
        del self.__label
        del self.__callback


class FileDialog(DPGItem):

    def __init__(self, label: str, on_select: Callable[[tuple[Path, ...]], None], extensions: Iterable[tuple[str, str]], default_path: str = "") -> None:
        super().__init__()

        def callback(_, app_data: dict[str, dict]):
            paths = app_data.get("selections").values()

            if len(paths) == 0:
                return

            on_select(tuple(Path(p) for p in paths))

        with dpg.file_dialog(
                label=label,
                callback=callback,
                directory_selector=False,
                show=False,
                width=1200,
                height=800,
                default_path=default_path,
                modal=True
        ) as f:
            self.setItemID(f)

            for extension, text in extensions:
                dpg.add_file_extension(f".{extension}", color=(255, 160, 80, 255), custom_text=f"[{text}]")


class DragLine(VariableDPGItem[float], Placeable):
    DEFAULT_COLOR = (255, 0X74, 0)

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None) -> None:
        super().__init__()
        self.__is_vertical = is_vertical
        self.__on_change = None if on_change is None else lambda: on_change(self.getValue())

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_drag_line(
            color=self.DEFAULT_COLOR,
            vertical=self.__is_vertical,
            callback=self.__on_change,
            parent=parent_id
        ))

    def _cleanup(self) -> None:
        del self.__is_vertical
        del self.__on_change


class DragPoint(VariableDPGItem[tuple[float, float]], Placeable):
    DEFAULT_COLOR = (0, 0X74, 0xFF)

    def __init__(
            self,
            on_move: Callable[[tuple[float, float]], None] = None,
            *,
            default_value: tuple[float, float] = (0, 0),
            label: str = None,
            color: Color3i = DEFAULT_COLOR,
            thickness: float = 1.0

    ):
        super().__init__()

        self.__callback = None if on_move is None else lambda: on_move(self.getValue())
        self.__default_value = default_value
        self.__label = label
        self.__color = color
        self.__thickness = thickness

    def getValue(self) -> tuple[float, float]:
        value = super().getValue()
        x, y, *trash = value
        return x, y

    def setValue(self, value: tuple[float, float]) -> None:
        super().setValue((*value, 0, 0))

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(
            dpg.add_drag_point(
                label=self.__label,
                parent=parent_id,
                callback=self.__callback,
                default_value=self.__default_value,
                color=self.__color,
                thickness=self.__thickness
            )
        )

    def _cleanup(self) -> None:
        del self.__callback
        del self.__default_value,
        del self.__label
        del self.__color,
        del self.__thickness


class Axis(DPGItem, Placeable, Container):

    def __init__(self, axis_type: int) -> None:
        super().__init__()
        self.__type = axis_type

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_plot_axis(self.__type, parent=parent_id))

    def _cleanup(self) -> None:
        del self.__type


class LineSeries(VariableDPGItem[tuple[Iterable[float], Iterable[float]]], Placeable):

    def __init__(self, label: str = None) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.setItemID(dpg.add_line_series(tuple(), tuple(), label=self.__label, parent=parent_id))

    def _cleanup(self) -> None:
        del self.__label
