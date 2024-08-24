from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Optional

from dearpygui import dearpygui as dpg

type ItemID = int | str
type Color = tuple[int, int, int]


def makeFileDialog(label: str, on_select: Callable[[tuple[Path, ...]], None], extensions: Iterable[tuple[str, str]], default_path: str = "") -> ItemID:
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
        for extension, text in extensions:
            dpg.add_file_extension(f".{extension}", color=(255, 160, 80, 255), custom_text=f"[{text}]")

        return f


class DragLine:
    CANVAS_BORDER_COLOR = (255, 0X74, 0)

    def __init__(self, is_vertical: bool, on_change: Callable[[float], None] = None) -> None:
        self.__is_vertical = is_vertical
        self.__item_id: Optional[ItemID] = None
        self.__on_change = None if on_change is None else lambda x: on_change(dpg.get_value(x))

    def build(self) -> None:
        self.__item_id = dpg.add_drag_line(
            color=self.CANVAS_BORDER_COLOR,
            vertical=self.__is_vertical,
            callback=self.__on_change
        )

    def getValue(self) -> float:
        return dpg.get_value(self.__item_id)

    def setValue(self, value: float) -> None:
        dpg.set_value(self.__item_id, value)


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
