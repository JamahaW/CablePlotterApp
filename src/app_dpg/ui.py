from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Optional

from dearpygui import dearpygui as dpg

type ItemID = int | str
type Color = tuple[int, int, int]


class Item:

    def __init__(self) -> None:
        self.dpg_item_id: Optional[ItemID] = None

    def getItemID(self) -> ItemID:
        return self.dpg_item_id

    def configure(self, **kwargs) -> None:
        dpg.configure_item(self.dpg_item_id, **kwargs)

    def hide(self) -> None:
        dpg.hide_item(self.dpg_item_id)

    def show(self) -> None:
        dpg.show_item(self.dpg_item_id)

    def enable(self) -> None:
        dpg.enable_item(self.dpg_item_id)

    def disable(self) -> None:
        dpg.disable_item(self.dpg_item_id)


class ValueContainerItem[T](Item):
    def setValue(self, value: T) -> None:
        dpg.set_value(self.dpg_item_id, value)

    def getValue(self) -> T:
        return dpg.get_value(self.dpg_item_id)


class Slider[T: (float, int)](ValueContainerItem[T], ABC):

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

    @classmethod
    @abstractmethod
    def _make_slider(cls, **kwargs) -> ItemID:
        pass

    def build(self) -> None:
        self.dpg_item_id = self._make_slider(
            label=self.label,
            callback=self.callback,
            min_value=self.value_range[0],
            max_value=self.value_range[1],
            default_value=self.default_value
        )


class SliderInt(Slider[int]):

    @classmethod
    def _make_slider(cls, **kwargs) -> ItemID:
        return dpg.add_slider_int(**kwargs)


class SliderFloat(Slider[float]):

    @classmethod
    def _make_slider(cls, **kwargs) -> ItemID:
        return dpg.add_slider_double(**kwargs)


class Button(Item):

    def __init__(self, label: str, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.__label = label
        self.__callback = lambda: on_click()

    def build(self, **kwargs) -> None:
        self.dpg_item_id = dpg.add_button(
            label=self.__label,
            callback=self.__callback,
            **kwargs
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


class DragLine(ValueContainerItem[float]):
    CANVAS_BORDER_COLOR = (255, 0X74, 0)

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None) -> None:
        super().__init__()
        self.__is_vertical = is_vertical
        self.__on_change = None if on_change is None else lambda x: on_change(dpg.get_value(x))

    def build(self) -> None:
        self.dpg_item_id = dpg.add_drag_line(
            color=self.CANVAS_BORDER_COLOR,
            vertical=self.__is_vertical,
            callback=self.__on_change
        )


class CanvasLinePair:

    def __init__(self, is_vertical: bool, step) -> None:
        self.__positive_line = DragLine(is_vertical, self.__setHalfSize)
        self.__negative_line = DragLine(is_vertical, self.__setHalfSize)
        self.step = step

    def build(self) -> None:
        self.__positive_line.build()
        self.__negative_line.build()

    def __setHalfSize(self, half_size: float) -> None:
        half_size = abs(half_size) // self.step * self.step
        self.__positive_line.setValue(half_size)
        self.__negative_line.setValue(-half_size)

    def setSize(self, size: float) -> None:
        self.__setHalfSize(size / 2)

    def getSize(self) -> float:
        return self.__positive_line.getValue() * 2


class CanvasLines:

    def __init__(self, step: int) -> None:
        self.__width_lines = CanvasLinePair(False, step)
        self.__height_lines = CanvasLinePair(True, step)

    def build(self) -> None:
        self.__width_lines.build()
        self.__height_lines.build()

    def setSize(self, width: int, height: int) -> None:
        self.__width_lines.setSize(width)
        self.__height_lines.setSize(height)

    def getSize(self) -> tuple[float, float]:
        return self.__width_lines.getSize(), self.__height_lines.getSize()


class Axis(Item):

    def __init__(self, axis_type: int) -> None:
        super().__init__()
        self.__type = axis_type

    def build(self) -> None:
        self.dpg_item_id = dpg.add_plot_axis(self.__type)


class LineSeries(ValueContainerItem[tuple[Iterable[float], Iterable[float]]]):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.__label = label

    def build(self, axis: Axis) -> None:
        self.dpg_item_id = dpg.add_line_series(tuple(), tuple(), label=self.__label, parent=axis.getItemID())
