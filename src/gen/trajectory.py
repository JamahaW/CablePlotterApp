from dataclasses import dataclass
from typing import Optional
from typing import Sequence


@dataclass(frozen=True, kw_only=True)
class Trajectory:
    """Траектория перемещения"""

    x_positions: Sequence[int]
    """Позиции перемещений X"""
    y_positions: Sequence[int]
    """Позиции перемещений Y"""
    tool_id: int
    """Инструмент печати"""
    movement_speed: Optional[int] = None
    """Скорость перемещения (Переопределяет базовую)"""
