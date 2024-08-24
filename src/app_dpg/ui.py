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

    def __init__(self, is_vertical: bool, value: int = 0, *, color: Color = (0xFF, 0xFF, 0xFF), on_change: Callable[[int], None] = None) -> None:
        self.color = color
        self.__is_vertical = is_vertical
        self.__default_value = value
        self.__item_id: Optional[ItemID] = None
        self.__on_change = None if on_change is None else lambda x: on_change(dpg.get_value(x))

    def build(self) -> None:
        self.__item_id = dpg.add_drag_line(
            color=self.color,
            default_value=self.__default_value,
            vertical=self.__is_vertical,
            callback=self.__on_change
        )

    def getValue(self) -> float:
        return dpg.get_value(self.__item_id)

    def setValue(self, value: float) -> None:
        dpg.set_value(self.__item_id, value)
