"""Виртуальный интерпретатор"""

from __future__ import annotations

from os import PathLike
from typing import Callable
from typing import Optional

from bytelang.dto.content.environment import Environment
from bytelang.dto.content.primitive import PrimitiveType
from bytelang.impl.registries import PrimitivesRegistry
from bytelang.tools import FileTool


# TODO push/pop без конвертации типов (использование сырого байтового значения)
# TODO режим отладки и лог работы
class Interpreter:
    def __init__(self, env: Environment, primitives: PrimitivesRegistry, instructions: tuple[Callable[[Interpreter], None], ...]) -> None:
        self.i8 = primitives.get("i8")
        self.u8 = primitives.get("u8")
        self.i16 = primitives.get("i16")
        self.u16 = primitives.get("u16")
        self.i32 = primitives.get("i32")
        self.u32 = primitives.get("u32")
        self.i64 = primitives.get("i64")
        self.u64 = primitives.get("u64")
        self.f32 = primitives.get("f32")
        self.f64 = primitives.get("f64")

        self.gt_flag: bool = False
        self.ge_flag: bool = False
        self.lt_flag: bool = False
        self.le_flag: bool = False
        self.eq_flag: bool = False
        self.ne_flag: bool = False

        self.ip = 0

        self.__instructions: tuple[Callable[[Interpreter], None], ...] = instructions

        self.__primitive_instruction_index = env.profile.instruction_index
        self.__primitive_heap_pointer = env.profile.pointer_heap
        self.__primitive_program_pointer = env.profile.pointer_program

        self.__stack = bytearray()
        self.__running = False
        self.__exit_code = 0

        self.__program: Optional[bytearray] = None

    def compareIntegers(self, a: int, b: int):
        self.gt_flag = a > b
        self.ge_flag = a >= b
        self.lt_flag = a < b
        self.le_flag = a <= b
        self.eq_flag = a == b
        self.ne_flag = a != b

    def stackPushPrimitive(self, primitive: PrimitiveType, value: int | float) -> None:
        """Записать значение примитивного типа в стек"""
        self.__stack.extend((primitive.packer.pack(value)))

    def stackPopPrimitive(self, primitive: PrimitiveType) -> int | float:
        """Получить значение примитивного типа из стека"""
        b = bytearray(self.__stack.pop() for _ in range(primitive.size))
        return primitive.packer.unpack(b)[0]

    def ipVariableStackPop(self, primitive: PrimitiveType) -> None:
        """Записать значение примитивного типа из стека в переменную по IP"""
        self.addressWritePrimitive(self.ipReadHeapPointer(), primitive, self.stackPopPrimitive(primitive))

    def ipStackPush(self, primitive: PrimitiveType) -> None:
        """Отправить в стек значение примитивного типа по IP"""
        self.stackPushPrimitive(primitive, self.ipReadPrimitive(primitive))

    def addressWritePrimitive(self, address: int, primitive: PrimitiveType, value: int | float) -> None:
        """Запись примитивный тип по адресу"""
        primitive.packer.pack_into(self.__program, address, value)

    def addressReadPrimitive(self, address: int, primitive: PrimitiveType) -> int | float:
        """Считать примитивный тип по адресу"""
        return primitive.packer.unpack_from(self.__program, address)[0]

    def ipReadVariable(self, primitive: PrimitiveType) -> int | float:
        return self.addressReadPrimitive(self.ipReadHeapPointer(), primitive)

    def ipReadPrimitive(self, primitive: PrimitiveType) -> int | float:
        """Считать значение примитивного типа по IP"""
        p = self.ip
        self.ip += primitive.size
        return self.addressReadPrimitive(p, primitive)

    def ipReadInstructionIndex(self) -> int:
        """Получить индекс инструкции по IP"""
        return self.ipReadPrimitive(self.__primitive_instruction_index)

    def ipReadHeapPointer(self) -> int:
        """Получить указатель на кучу по IP"""
        return self.ipReadPrimitive(self.__primitive_heap_pointer)

    def setExitCode(self, code: int) -> None:
        self.__exit_code = code
        self.__running = False

    def run(self, bytecode_filepath: PathLike | str) -> int:
        self.gt_flag = False
        self.ge_flag = False
        self.lt_flag = False
        self.le_flag = False
        self.eq_flag = False
        self.ne_flag = False

        self.ip = 0
        self.__running = True
        self.__stack.clear()
        self.__program = bytearray(FileTool.readBytes(bytecode_filepath))

        self.ip = self.ipReadHeapPointer()

        while self.__running:
            self.__instructions[self.ipReadInstructionIndex()].__call__(self)

        return self.__exit_code

    @staticmethod
    def stdoutWrite(value: str) -> None:
        print(value, end="")
