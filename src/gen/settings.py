from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Settings:
    """Настройки генерации кода"""

    speed: int
    """Скорость перемещения"""
    end_speed: int
    """Скорость перемещения при перемещении домой"""
    tool_none: int
    """код выбора инструмента с печатью, инструмент 1"""
    disconnect_distance_mm: int
    """критическое расстояние между вершинами"""
    tool_change_duration_ms: int
    """Задержка при смене инструмента"""
