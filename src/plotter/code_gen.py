from os import PathLike
from pathlib import Path
from typing import Iterable
from typing import Optional

from bytelang import ByteLang
from bytelang import CompileResult
from bytelang.processors import LogFlag
from bytelang.tools import FileTool
from bytelang.tools import StringBuilder
from plotter.instructions import begin_code
from plotter.instructions import enc_code
from plotter.instructions import move_to
from plotter.instructions import set_motors_speed

RES_FOLDER = Path(r"A:\Program\Python3\CablePlotterApp\res")


class PlotterCodeGenerator:
    SOURCE_FILE = RES_FOLDER / "out/test.bls"

    def __init__(self) -> None:
        BL_FOLDER = RES_FOLDER / "bytelang"

        self.bytelang = ByteLang()
        self.bytelang.environment_registry.setFolder(BL_FOLDER / "env")
        self.bytelang.profile_registry.setFolder(BL_FOLDER / "profiles")
        self.bytelang.package_registry.setFolder(BL_FOLDER / "packages")
        self.bytelang.primitives_registry.setFile(BL_FOLDER / "std.json")

    def __generateCode(self, positions: Iterable[tuple[int, int]]):
        builder = StringBuilder()
        builder.append(begin_code()).append(set_motors_speed(8))

        for x, y in positions:
            builder.append(move_to(x, y))

        builder.append(enc_code())
        FileTool.save(self.SOURCE_FILE, builder.toString())

    def __getLog(self, result: Optional[CompileResult], log_flag: LogFlag = LogFlag.ALL) -> str:
        if result is None:
            return self.bytelang.getErrorsLog()
        else:
            return result.getInfoLog(log_flag)

    def run(self, positions: Iterable[tuple[int, int]], out_file: PathLike | str) -> str:
        # self.__generateCode(positions)
        result = self.bytelang.compile(self.SOURCE_FILE, out_file)
        return self.__getLog(result)


if __name__ == '__main__':
    path = [
        (100, 100),
        (100, -100),
        (-100, -100),
        (-100, 100),
        (100, 100),
    ]

    log = PlotterCodeGenerator().run(path, RES_FOLDER / "out/test.blc")
    print(log)
