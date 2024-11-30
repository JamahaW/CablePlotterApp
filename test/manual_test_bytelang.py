from bytelang.main import ByteLang
from tools.string import FixedStringIO

bytelang = ByteLang.simpleSetup(r"A:\Projects\Вертикальный тросовый плоттер\Код\CablePlotterApp\res\bytelang")

SOURCE = """
.env esp32

.def MY_MACRO 123 

.ptr u32 my_var 0xAB_CD_EF_12

my_mark:

delay_ms my_mark 


quit    
"""

with open("out.blc", "wb") as bytecode_stream:
    result = bytelang.compile(FixedStringIO(SOURCE), bytecode_stream)
    print(result.getMessage())
