from pathlib import Path

from bytelang import ByteLang
from bytelang import EnvironmentsRegistry
from bytelang import PackageRegistry
from bytelang import PrimitivesRegistry
from bytelang import ProfileRegistry

bytelang_path = Path(r"A:\Projects\Вертикальный тросовый плоттер\Код\CablePlotterApp\res\bytelang")

primitives_registry = PrimitivesRegistry(bytelang_path / "std.json")
profile_registry = ProfileRegistry(bytelang_path / "profiles", "json", primitives_registry)
package_registry = PackageRegistry(bytelang_path / "packages", "blp", primitives_registry)
environments_registry = EnvironmentsRegistry(bytelang_path / "env", "json", profile_registry, package_registry)

bytelang = ByteLang(primitives_registry, environments_registry)

with open("test.bls", "rt") as source_stream:
    with open("out.blc", "wb") as bytecode_stream:
        result = bytelang.compile(source_stream, bytecode_stream)

        log = result.getInfoLog()

        print(log)
