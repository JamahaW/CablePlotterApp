from __future__ import annotations

import math
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Sequence
from typing import TextIO

from bytelang.main import ByteLang
from gen.settings import Settings
from gen.trajectory import Trajectory
from tools.filetool import FileTool


class State:
    """Статус (Состояние) генератора"""

    @staticmethod
    def __calcTotalStepCount(contours: Sequence[Trajectory]) -> int:
        return sum(map(lambda c: len(c.x_positions), contours))

    def __init__(self, contours: Sequence[Trajectory], config: Settings):
        self.global_total_step_count: int = self.__calcTotalStepCount(contours)
        """глобальное суммарное количество перемещений (шаги)"""
        self.last_speed: int = config.speed

        self.global_current_step_index: int = 0
        """глобальный индекс текущего шага"""
        self.global_last_progress: int = -1
        """Предыдущий уровень прогресса"""

        self.last_x: int = 0
        """Последняя позиция X"""
        self.last_y: int = 0
        """Последняя позиция Y"""


@dataclass(frozen=True)
class CodeGenerator:
    """Генератор кода"""

    setup: str
    """Код настройки"""
    start: str
    """Стартовый код"""
    on_contour_begin: str
    """В начале контура"""

    on_new_position: str
    """Код смене позиции"""
    on_disconnect: str
    """Код при смене инструмента"""
    on_update_progress: str
    """Код при обновлении прогресса"""

    on_contour_end: str
    """В конце контура"""
    end: str
    """Завершающий код"""

    @classmethod
    def load(cls, codes: PathLike | str) -> CodeGenerator:
        return CodeGenerator(**{
            handler_path.stem: FileTool.read(handler_path)
            for handler_path in Path(codes).glob(f"*.{ByteLang.SOURCE_EXTENSION}")
        })

    def __processTrajectory(self, stream: TextIO, config: Settings, trajectory: Trajectory, state: State) -> None:
        paint_move_speed = config.speed if trajectory.movement_speed is None else trajectory.movement_speed

        stream.write(self.on_contour_begin.format(
            speed=paint_move_speed,
            tool_paint=trajectory.tool_id
        ))

        for step_index, position in enumerate(zip(trajectory.x_positions, trajectory.y_positions)):
            self.__processStep(config, trajectory, state, step_index, stream, position)

        stream.write(self.on_contour_end)

    def __processStep(self, config: Settings, trajectory: Trajectory, state: State, step_index: int, stream: TextIO, position: tuple[int, int]):
        x, y = position
        state.global_current_step_index += 1

        if step_index > 0:
            state.last_x = trajectory.x_positions[step_index - 1]
            state.last_y = trajectory.y_positions[step_index - 1]

        delta_mm = math.hypot(x - state.last_x, y - state.last_y)

        if delta_mm > config.disconnect_distance_mm:
            stream.write(self.on_disconnect.format(
                tool_paint=trajectory.tool_id,
                tool_none=config.tool_none,
                tool_change_duration_ms=config.tool_change_duration_ms,
                x=x,
                y=y
            ))
        else:
            stream.write(self.on_new_position.format(x=x, y=y))

        current_progress = state.global_current_step_index * 100 // state.global_total_step_count

        if current_progress != state.global_last_progress:
            stream.write(self.on_update_progress.format(progress=current_progress))
            state.global_last_progress = current_progress

    def run(self, stream: TextIO, config: Settings, contours: Sequence[Trajectory]) -> None:
        status = State(contours, config)

        stream.write(self.setup)

        stream.write(self.start.format(
            speed=config.speed,
            tool_none=config.tool_none
        ))

        for contour in contours:
            self.__processTrajectory(stream, config, contour, status)

        stream.write(self.end.format(
            end_speed=config.end_speed,
            tool_none=config.tool_none
        ))
