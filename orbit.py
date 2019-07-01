#! /usr/bin/env python python

import arcade
import math
import random
from pathlib import Path
from typing import List, Tuple
# Size of the screen
SCREEN_WIDTH: int = 1000
SCREEN_HEIGHT: int = 800
SCREEN_TITLE: str = "Orbit"

PARTICLE_FILE = Path('./images/asteroid-icon.png')
PARTICLE_SCALING = 1.0 / 70
PARTICLE_MAX_SPEED: int = 5  # divide by 10
PARTICLE_RADIUS: int = 7
PARTICLE_MASS: int = 10

IMPACT_OVERLAP_TOLERANCE = 0.1


class Vector2d:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, v: 'Vector2d') -> 'Vector2d':
        return Vector2d(self.x + v.x, self.y + v.y)

    def __iadd__(self, v: 'Vector2d') -> 'Vector2d':
        self.x += v.x
        self.y += v.y
        return self

    def __sub__(self, v: 'Vector2d') -> 'Vector2d':
        return Vector2d(self.x - v.x, self.y - v.y)

    def __mul__(self, m: float) -> 'Vector2d':
        return Vector2d(self.x * m, self.y * m)

    def __div__(self, m: float) -> 'Vector2d':
        if m == 0.0:
            return Vector2d(math.inf, math.inf)
        return Vector2d(self.x / m, self.y / m)

    def __repr__(self):
        return 'vector(x->' + str(self.x) + ', y->' + str(self.y) + ')'

    def __getitem__(self, index) -> float:
        return self.x if index == 0 else self.y

    def get_coord(self) -> Tuple[float, float]:
        return self.x, self.y

    def to_polar(self) -> 'VectorPolar':
        return VectorPolar(math.sqrt(self.x**2 + self.y**2), math.atan2(self.y, self.x))

    def rotation_transform(self, phi) -> 'Vector2d':
        v_polar = self.to_polar()
        v_polar.phi += phi
        return v_polar.to_cartesian()


class VectorPolar:
    def __init__(self, rho: float, phi: float):
        self.rho = rho
        self.phi = phi

    def __add__(self, v: 'VectorPolar') -> 'VectorPolar':
        # can't be bothered to implement correctly
        return (self.to_cartesian() + v.to_cartesian()).to_polar()

    def __sub__(self, v: 'VectorPolar') -> 'VectorPolar':
        # can't be bothered to implement correctly
        return (self.to_cartesian() - v.to_cartesian()).to_polar()

    def __mul__(self, m: float) -> 'VectorPolar':
        return VectorPolar(self.rho * m, self.phi)

    def __div__(self, m: float) -> 'VectorPolar':
        if m == 0.0:
            return VectorPolar(math.inf, math.inf)
        return VectorPolar(self.rho / m, self.phi)

    def __repr__(self):
        return 'vector(rho->' + str(self.rho) + ', phi->' + str(self.phi) + ')'

    def to_cartesian(self) -> Vector2d:
        return Vector2d(self.rho * math.cos(self.phi), self.rho * math.sin(self.phi))


class FieldIter:
    def __init__(self, field: 'GravitationalField'):
        self.field = field
        self.x = 0
        self.y = 0

    def __next__(self) -> Tuple[int, int]:
        self.x += 1
        if self.x >= self.field._x:
            self.x = 0
            self.y += 1
            if self.y >= self.field._y:
                raise StopIteration
        return self.x, self.y


class GravitationalField:
    """
    gravitational field as 2d array
    """
    def __init__(self, inital_value: float = 0):
        """
        constructor

        :param inital_value: intial field values, defaults to 0
        """
        self._x = SCREEN_WIDTH
        self._y = SCREEN_HEIGHT
        self.field: List[list] = [x[:] for x in [[inital_value] * self._y] * self._x]

    def __iter__(self):
        return FieldIter(self)

    def get_value(self, x: int, y: int) -> float:
        return self.field[x][y]

    def set_value(self, x: int, y: int, value: float):
        self.field[x][y] = value


class Particle(arcade.sprite.Sprite):
    """
    single particle in the simulation
    """
    # rather than setting the impact check and having to reset it, toggle parity and
    # impact_check == impact_parity gives you the check status
    impact_parity: bool = True
    count = 0

    def __init__(self, x: float, y: float, delta_x: float, delta_y: float, size: int):
        super().__init__(PARTICLE_FILE, PARTICLE_SCALING*size)
        self.name = 'particle' + str(Particle.count)
        Particle.count += 1

        self.particle_position = Vector2d(x, y)
        self.particle_velocity = Vector2d(delta_x, delta_y)
        self.sync_coord()

        self.impact_check: bool = not Particle.impact_parity
        self.impact_velocity: Vector2d = None
        self.size = PARTICLE_RADIUS
        self.mass = size

    @staticmethod
    def generate() -> 'Particle':
        """
        generates a new particle with random location and particle_velocity

        :return: new particle
        """
        return Particle(
            random.randrange(PARTICLE_RADIUS, SCREEN_WIDTH - PARTICLE_RADIUS),
            random.randrange(PARTICLE_RADIUS, SCREEN_HEIGHT - PARTICLE_RADIUS),
            random.randrange(-PARTICLE_MAX_SPEED, PARTICLE_MAX_SPEED)/10.0,
            random.randrange(-PARTICLE_MAX_SPEED, PARTICLE_MAX_SPEED)/10.0,
            PARTICLE_RADIUS)

    def checked(self) -> bool:
        """
        determines if particle has already been checked for impacts

        :return: [description]
        """
        return self.impact_check == Particle.impact_parity

    def sync_coord(self) -> None:
        self.center_x, self.center_y = self.particle_position.get_coord()
        self.change_x, self.change_y = self.particle_velocity.get_coord()

    def update(self) -> None:
        """
        updates particle's location
        """
        self.particle_position += self.particle_velocity
        self.sync_coord()


class ImpactHelper:

    @staticmethod
    def point_distance(point_a: 'Vector2d', point_b: 'Vector2d') -> float:
        delta = point_a - point_b
        return round(math.sqrt((delta.x)**2 + (delta.y)**2))

    @staticmethod
    def particle_distance(particle_1: 'Particle', particle_2: 'Particle') -> float:
        return ImpactHelper.point_distance(particle_1.particle_position, particle_2.particle_position)

    @staticmethod
    def is_particle_impact(particle_1: Particle, particle_2: Particle) -> bool:
        return ImpactHelper.particle_distance(particle_1, particle_2) <= particle_1.size + particle_2.size

    @staticmethod
    def remove_overlap(particle_1: Particle, particle_2: Particle) -> None:
        if ((particle_1.size + particle_2.size) - (ImpactHelper.particle_distance(particle_1, particle_2)))/2 <= IMPACT_OVERLAP_TOLERANCE:
            return  # ignore very small overlap

        # rewinding till particles have just started touching, in order to later solve the impact
        dx = particle_1.particle_position.x - particle_2.particle_position.x
        vx = particle_1.particle_velocity.x - particle_2.particle_velocity.x
        dy = particle_1.particle_position.y - particle_2.particle_position.y
        vy = particle_1.particle_velocity.y - particle_2.particle_velocity.y
        r = particle_1.size + particle_2.size

        # finding how far to "rewind"
        rewind = (math.sqrt((-2 * dx * vx - 2 * dy * vy)**2 - 4*(vx**2 + vy**2) * (dx**2 + dy**2 - r**2)) + 2 * dx * vx + 2 * dy * vy)/(2 * (vx**2 + vy**2))

        # updating positions
        particle_1.particle_position = particle_1.particle_position - particle_1.particle_velocity*rewind
        particle_2.particle_position = particle_2.particle_position - particle_2.particle_velocity*rewind

    @staticmethod
    def particle_impact_transformation(particle_1: Particle, particle_2: Particle):
        impact_angle = (particle_1.particle_velocity - particle_2.particle_velocity).to_polar().phi
        velocity_a = particle_1.particle_velocity.rotation_transform(impact_angle)
        velocity_b = particle_2.particle_velocity.rotation_transform(impact_angle)
        return velocity_a, velocity_b, impact_angle

    @staticmethod
    def particle_impact_energy(particle_1: Particle, velocity_1: Vector2d, particle_2: Particle, velocity_2: Vector2d, impact_angle: float):
        m1 = particle_1.mass
        m2 = particle_2.mass

        impact_velocity_1 = Vector2d((m1 - m2)/(m1 + m2) * velocity_1.x + 2 * m2/(m1 + m2) * velocity_2.x, velocity_1.y)
        impact_velocity_2 = Vector2d(2 * m2/(m1 + m2) * velocity_1.x - (m1 - m2)/(m1 + m2) * velocity_2.x, velocity_2.y)

        particle_1.impact_velocity += impact_velocity_1.rotation_transform(-impact_angle)
        particle_2.impact_velocity += impact_velocity_2.rotation_transform(-impact_angle)


class Orbit(arcade.Window):
    def __init__(self):
        self.particle_list = None
        self.field = None
        self.total_energy = None
        return super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.particle_list = arcade.SpriteList()
        self.field = GravitationalField()
        self.total_energy = 0

    def update_field(self):
        pass

    def particle_impact(self, particle_1):
        particle_1.impact_check = Particle.impact_parity

        if particle_1.particle_position.x < particle_1.size or particle_1.particle_position.x > SCREEN_WIDTH - particle_1.size:
            particle_1.impact_velocity = Vector2d(-1 * particle_1.particle_velocity.x, particle_1.particle_velocity.y)

        if particle_1.particle_position.y < particle_1.size or particle_1.particle_position.y > SCREEN_HEIGHT - particle_1.size:
            particle_1.impact_velocity = Vector2d(particle_1.particle_velocity.x, -1 * particle_1.particle_velocity.y)

        particle_2: Particle = None
        for particle_2 in self.particle_list:
            if not particle_2.checked() and ImpactHelper.is_particle_impact(particle_1, particle_2):
                ImpactHelper.remove_overlap(particle_1, particle_2)

                particle_1.impact_velocity = Vector2d(0, 0)
                particle_2.impact_velocity = Vector2d(0, 0)
                velocity_1, velocity_2, impact_angle = ImpactHelper.particle_impact_transformation(particle_1, particle_2)
                ImpactHelper.particle_impact_energy(particle_1, velocity_1, particle_2, velocity_2, impact_angle)

        if particle_1.impact_velocity is not None:
            particle_1.particle_velocity.x = particle_1.impact_velocity.x
            particle_1.particle_velocity.y = particle_1.impact_velocity.y
            particle_1.update()

        particle_1.impact_velocity = None

    def on_update(self, delta_time: float):
        self.particle_list.update()
        self.total_energy = 0

        particle: Particle
        for particle in self.particle_list:
            self.particle_impact(particle)
            self.total_energy += ImpactHelper.point_distance(Vector2d(0, 0), particle.particle_velocity)**2 * particle.mass

        Particle.impact_parity = not Particle.impact_parity

    def on_draw(self):
        arcade.start_render()
        self.particle_list.draw()

        output = f"Particles: {Particle.count} Energy: {self.total_energy}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.SPACE:
            self.particle_list.append(Particle.generate())


if __name__ == "__main__":
    game = Orbit()
    game.setup()
    game.set_update_rate(1/200)
    arcade.run()
