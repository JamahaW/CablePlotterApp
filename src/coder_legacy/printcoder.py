from dataclasses import dataclass
from math import cos
from math import hypot
from math import pi
from math import radians
from math import sin

import numpy as np


@dataclass
class Vector2:
    x: int | float
    y: int | float

    def toTuple(self) -> tuple[int | float, int | float]:
        return self.x, self.y


def mix(a: float, b: float, t: float) -> float:
    return a * t + (1.0 - t) * b


def vecMix(pos: Vector2, old: Vector2, t: float) -> Vector2:
    return Vector2(
        mix(pos.x, old.x, t),
        mix(pos.y, old.y, t)
    )


class VertexGenerator:

    @staticmethod
    def scale(source: list[Vector2], scale: Vector2):
        return [
            Vector2(v.x * scale.x, v.y * scale.y)
            for v in source
        ]

    @staticmethod
    def move(source: list[Vector2], offset: Vector2):
        return [
            Vector2(v.x + offset.x, v.y + offset.y)
            for v in source
        ]

    @staticmethod
    def rotate(source: list[Vector2], angle: float):
        r = radians(angle)
        cos_a = cos(r)
        sin_a = sin(r)

        return [
            Vector2(cos_a * v.x - sin_a * v.y, sin_a * v.x + cos_a * v.y)
            for v in source
        ]

    @staticmethod
    def removeNear(vex: list[Vector2], delta: float = 1) -> list[Vector2]:
        if len(vex) == 0:
            return vex

        ret = [vex[0]]

        for cur in vex[1:]:
            last = ret[-1]

            if hypot(cur.x - last.x, cur.y - last.y) > delta:
                ret.append(Vector2(cur.x, cur.y))

        return ret

    @staticmethod
    def findFarIndices(vex: list[Vector2], far=20):
        return {
            i
            for i in range(len(vex) - 1)
            if hypot(vex[i].x - vex[i + 1].x, vex[i].y - vex[i + 1].y) > far
        }

    @staticmethod
    def nearDistSort(vertices: list[Vector2]) -> list:

        vex = [
            v.toTuple()
            for v in vertices
        ]

        path = [vex[0]]

        unvisited_vertices = np.array(vex[1:])

        while unvisited_vertices.shape[0] > 0:
            current_vertex = path[-1][::-1]
            distances = np.linalg.norm(unvisited_vertices - current_vertex, axis=1)
            nearest_index = np.argmin(distances)
            nearest = unvisited_vertices[nearest_index]
            path.append(tuple(nearest[::-1]))
            unvisited_vertices = np.delete(unvisited_vertices, nearest_index, axis=0)

        return [
            Vector2(p[0], p[1])
            for p in path
        ]

    #

    @staticmethod
    def spiral(radius: int, steps: int, k=1.0) -> list[Vector2]:
        K2PI_P = 2 * k * pi / steps
        R_P = radius / steps

        return [
            Vector2(sin(a * K2PI_P) * a * R_P, cos(a * K2PI_P) * a * R_P)
            for a in range(steps + 1)
        ]

    @staticmethod
    def circle(radius: int, steps: int) -> list[Vector2]:
        K2PI_P = 2 * pi / steps

        return [
            Vector2(sin(a * K2PI_P) * radius, cos(a * K2PI_P) * radius)
            for a in range(steps)
        ]

    @classmethod
    def rect(cls, width: int, height: int, steps: int) -> list[Vector2]:
        W = width / 2
        H = height / 2

        steps_h = int(height * steps / width)

        p1 = W, H
        p2 = W, -H
        p3 = -W, -H
        p4 = -W, H

        draw_data = (
            (p1, p2, steps_h),
            (p2, p3, steps),
            (p3, p4, steps_h),
            (p4, p1, steps)
        )

        ret = list()

        for (xa, ya), (xb, yb), st in draw_data:
            ret.extend(cls.line(Vector2(xa, ya), Vector2(xb, yb), st))

        return ret

    @staticmethod
    def line(pos1: Vector2, pos2: Vector2, steps: int) -> list[Vector2]:
        return [
            vecMix(pos1, pos2, t / steps)
            for t in range(steps + 1)
        ]

    @classmethod
    def image(cls, path: str) -> list[Vector2]:
        pass
