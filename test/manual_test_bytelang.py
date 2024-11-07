from io import StringIO

from bytelang import ByteLang

bytelang = ByteLang.simpleSetup(r"A:\Projects\Вертикальный тросовый плоттер\Код\CablePlotterApp\res\bytelang")


class FixedStringIO(StringIO):
    @property
    def name(self) -> str:
        return self.__class__.__name__


SOURCE = """
.env esp32_env

.def MY_MACRO 123 

.ptr u32 my_var 0xAB_CD_EF_12

my_mark:

delay_ms MY_MACRO 
quit    
"""

with open("out.blc", "wb") as bytecode_stream:
    result = bytelang.compile(FixedStringIO(SOURCE), bytecode_stream)
    print(result.getMessage())
