from bytelang import ByteLang

bytelang = ByteLang.simpleSetup(r"A:\Projects\Вертикальный тросовый плоттер\Код\CablePlotterApp\res\bytelang")

with open("test.bls", "rt") as source_stream:
    with open("out.blc", "wb") as bytecode_stream:
        result = bytelang.compile(source_stream, bytecode_stream)
        print(result.getMessage())
