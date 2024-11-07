from os import PathLike
from pathlib import Path
from typing import Iterable
from typing import Optional

from bytelang import ByteLang
from bytelang import CompileResultLegacy
from bytelang import PrimitivesRegistry
from bytelang.impl.result import LogFlag
from bytelang.tools import FileTool
from bytelang.tools import StringBuilder
from plotter.instructions import begin_code
from plotter.instructions import enc_code
from plotter.instructions import move_to
from plotter.instructions import set_motors_speed

RES_FOLDER = Path(r"A:\Projects\Вертикальный тросовый плоттер\Код\CablePlotterApp\res")


class PlotterCodeGenerator:

    def __init__(self, bytelang: ByteLang) -> None:
        self.SOURCE_FILEPATH = RES_FOLDER / "out/test.bls"
        BL_FOLDER = RES_FOLDER / "bytelang"

        self.bytelang = bytelang
        self.bytelang.__environment_registry.setFolder(BL_FOLDER / "env")
        self.bytelang.__profile_registry.setFolder(BL_FOLDER / "profiles")
        self.bytelang.package_registry.setFolder(BL_FOLDER / "packages")
        self.bytelang.__primitives_registry.setFile(BL_FOLDER / "std.json")

    def __generateCode(self, positions: Iterable[tuple[int, int]]):
        builder = StringBuilder()
        builder.append(begin_code()).append(set_motors_speed(8))

        for x, y in positions:
            builder.append(move_to(x, y))

        builder.append(enc_code())
        FileTool.save(self.SOURCE_FILEPATH, builder.toString())

    def __getLog(self, result: Optional[CompileResultLegacy], log_flag: LogFlag = LogFlag.ALL) -> str:
        if result is None:
            return self.bytelang.getErrorsLog()
        else:
            return result.getInfoLog(log_flag)

    def run(self, positions: Iterable[tuple[int, int]], out_file: PathLike | str) -> str:
        # self.__generateCode(positions)

        result = self.bytelang.compile(self.SOURCE_FILEPATH, out_file)
        return self.__getLog(result)


if __name__ == '__main__':
    path = [
    ]

    primitives_registry = PrimitivesRegistry()
    profile_registry = ProfileRegistry(, "json", primitives_registry
    package_registry = PackageRegistry("blp", primitives_registry)

    bytelang = ByteLang(
        primitives_registry,
        profile_registry,
        package_registry,
        EnvironmentsRegistry("json", profile_registry, package_registry)
    )

    code_generator = PlotterCodeGenerator(bytelang)

    log = code_generator.run(path, RES_FOLDER / "out/test.blc")

    print(log)
