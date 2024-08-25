from abc import ABC
from pathlib import Path
from typing import Callable
from typing import Iterable

from dearpygui import dearpygui as dpg

from app_dpg.ui.abc import ContainerItem
from app_dpg.ui.abc import Item
from app_dpg.ui.abc import ItemID
from app_dpg.ui.abc import PlaceableItem
from app_dpg.ui.abc import VariableItem


class Group(ContainerItem):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__kwargs = kwargs

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_group(parent=parent_id, **self.__kwargs)


class Header(ContainerItem):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_collapsing_header(label=self.__label, parent=parent_id)


class Plot(ContainerItem):

    def placeRaw(self, parent_id: ItemID) -> None:
        with dpg.plot(width=-1, height=-1, equal_aspects=True, anti_aliased=True) as plot:
            self.dpg_item_id = plot
            dpg.add_plot_legend(horizontal=True)


class Slider[T: (float, int)](VariableItem[T], PlaceableItem, ABC):

    def __init__(
            self,
            value_range: tuple[T, T],
            label: str = None,
            on_change: Callable[[T], None] = None,
            *,
            default_value: T = 0
    ):
        super().__init__()
        self.callback = None if on_change is None else lambda: on_change(self.getValue())
        self.label = label
        self.value_range = value_range
        self.default_value = default_value


class SliderInt(Slider[int]):

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_slider_int(
            label=self.label,
            callback=self.callback,
            min_value=self.value_range[0],
            max_value=self.value_range[1],
            parent=parent_id,
            default_value=self.default_value
        )


class SliderFloat(Slider[float]):

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_slider_double(
            label=self.label,
            callback=self.callback,
            min_value=self.value_range[0],
            max_value=self.value_range[1],
            parent=parent_id,
            default_value=self.default_value
        )


class Button(Item, PlaceableItem):

    def __init__(self, label: str, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.__label = label
        self.__callback = lambda: on_click()

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_button(
            label=self.__label,
            callback=self.__callback,
            parent=parent_id
        )


class FileDialog(Item):

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
            self.dpg_item_id = f

            for extension, text in extensions:
                dpg.add_file_extension(f".{extension}", color=(255, 160, 80, 255), custom_text=f"[{text}]")


class DragLine(VariableItem[float], PlaceableItem):
    CANVAS_BORDER_COLOR = (255, 0X74, 0)

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None) -> None:
        super().__init__()
        self.__is_vertical = is_vertical
        self.__on_change = None if on_change is None else lambda x: on_change(dpg.get_value(x))

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_drag_line(
            color=self.CANVAS_BORDER_COLOR,
            vertical=self.__is_vertical,
            callback=self.__on_change,
            parent=parent_id
        )


class Axis(Item, PlaceableItem):

    def __init__(self, axis_type: int) -> None:
        super().__init__()
        self.__type = axis_type

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_plot_axis(self.__type, parent=parent_id)


class LineSeries(VariableItem[tuple[Iterable[float], Iterable[float]]], PlaceableItem):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def placeRaw(self, parent_id: ItemID) -> None:
        self.dpg_item_id = dpg.add_line_series(tuple(), tuple(), label=self.__label, parent=parent_id)
