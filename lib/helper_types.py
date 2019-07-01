from __future__ import annotations

import math
from typing import Tuple


class Vector2d:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, v: Vector2d) -> Vector2d:
        return Vector2d(self.x + v.x, self.y + v.y)

    def __iadd__(self, v: Vector2d) -> Vector2d:
        self.x += v.x
        self.y += v.y
        return self

    def __sub__(self, v: Vector2d) -> Vector2d:
        return Vector2d(self.x - v.x, self.y - v.y)

    def __mul__(self, m: float) -> Vector2d:
        return Vector2d(self.x * m, self.y * m)

    def __div__(self, m: float) -> Vector2d:
        if m == 0.0:
            return Vector2d(math.inf, math.inf)
        return Vector2d(self.x / m, self.y / m)

    def __repr__(self) -> str:
        return 'vector(x->' + str(self.x) + ', y->' + str(self.y) + ')'

    def __getitem__(self, index: int) -> float:
        return self.x if index == 0 else self.y

    def get_coord(self) -> Tuple[float, float]:
        return self.x, self.y

    def to_polar(self) -> VectorPolar:
        return VectorPolar(math.sqrt(self.x**2 + self.y**2), math.atan2(self.y, self.x))

    def rotation_transform(self, phi) -> Vector2d:
        v_polar = self.to_polar()
        v_polar.phi += phi
        return v_polar.to_cartesian()


class VectorPolar:
    def __init__(self, rho: float, phi: float):
        self.rho = rho
        self.phi = phi

    def __add__(self, v: VectorPolar) -> VectorPolar:
        # can't be bothered to implement correctly
        return (self.to_cartesian() + v.to_cartesian()).to_polar()

    def __sub__(self, v: VectorPolar) -> VectorPolar:
        # can't be bothered to implement correctly
        return (self.to_cartesian() - v.to_cartesian()).to_polar()

    def __mul__(self, m: float) -> VectorPolar:
        return VectorPolar(self.rho * m, self.phi)

    def __div__(self, m: float) -> VectorPolar:
        if m == 0.0:
            return VectorPolar(math.inf, math.inf)
        return VectorPolar(self.rho / m, self.phi)

    def __repr__(self):
        return 'vector(rho->' + str(self.rho) + ', phi->' + str(self.phi) + ')'

    def to_cartesian(self) -> Vector2d:
        return Vector2d(self.rho * math.cos(self.phi), self.rho * math.sin(self.phi))
