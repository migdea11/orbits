#! /usr/bin/env python python

import arcade
import random

import lib.particle as particle_lib
import lib.impact_calculations as ImpactHelper
from lib.helper_types import Vector2d
from lib.particle import Particle

# Size of the screen
SCREEN_WIDTH: int = 1000
SCREEN_HEIGHT: int = 800
SCREEN_TITLE: str = "Orbit"

GRAVITATIONAL_CONST_2D = 1  # TODO update


# class FieldIter:
#     def __init__(self, field: 'GravitationalField'):
#         self.field = field
#         self.x = 0
#         self.y = 0

#     def __next__(self) -> Tuple[int, int]:
#         self.x += 1
#         if self.x >= self.field._x:
#             self.x = 0
#             self.y += 1
#             if self.y >= self.field._y:
#                 raise StopIteration
#         return self.x, self.y


# class GravitationalField:
#     """
#     gravitational field as 2d array
#     """
#     def __init__(self, inital_value: float = 0):
#         """
#         constructor

#         :param inital_value: intial field values, defaults to 0
#         """
#         self._x = SCREEN_WIDTH
#         self._y = SCREEN_HEIGHT
#         self.field: List[list] = [x[:] for x in [[inital_value] * self._y] * self._x]

#     def __iter__(self):
#         return FieldIter(self)

#     def get_value(self, x: int, y: int) -> float:
#         return self.field[x][y]

#     def set_value(self, x: int, y: int, value: float):
#         self.field[x][y] = value


class Orbit(arcade.Window):
    def __init__(self):
        self.particle_list = None
        self.field = None
        self.total_energy = None
        return super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.particle_list = arcade.SpriteList()
        self.total_energy = 0

    @staticmethod
    def generate() -> 'Particle':
        """
        generates a new particle with random location and particle_velocity

        :return: new particle
        """
        return Particle(
            random.randrange(particle_lib.PARTICLE_RADIUS, SCREEN_WIDTH - particle_lib.PARTICLE_RADIUS),
            random.randrange(particle_lib.PARTICLE_RADIUS, SCREEN_HEIGHT - particle_lib.PARTICLE_RADIUS),
            random.randrange(-particle_lib.PARTICLE_MAX_SPEED, particle_lib.PARTICLE_MAX_SPEED)/10.0,
            random.randrange(-particle_lib.PARTICLE_MAX_SPEED, particle_lib.PARTICLE_MAX_SPEED)/10.0,
            particle_lib.PARTICLE_RADIUS)

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
            self.particle_list.append(Orbit.generate())


if __name__ == "__main__":
    game = Orbit()
    game.setup()
    game.set_update_rate(1/200)
    arcade.run()
