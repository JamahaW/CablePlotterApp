from pathlib import Path
from typing import Callable
from typing import Iterable

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
