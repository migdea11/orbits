import arcade
from arcade.examples.frametime_plotter import FrametimePlotter
import math
import random
from typing import List
# Size of the screen
SCREEN_WIDTH: int = 1000
SCREEN_HEIGHT: int = 800
SCREEN_TITLE: str = "Orbit Trial"

PARTICLE_MAX_SPEED: int = 20  # divide by 10
PARTICLE_RADIUS: int = 5
PARTICLE_MASS: int = 10


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

    def to_polar(self) -> 'VectorPolar':
        return VectorPolar(math.sqrt(self.x**2 + self.y**2), math.atan2(self.y, self.x))

    def rotation_transform(self, phi) -> 'Vector2d':
        v_polar = self.to_polar()
        # print('polar', v_polar, phi)
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


class GravitationalField:
    """
    gravitational field as 2d array
    """
    def __init__(self, inital_value: float = 0):
        """
        constructor

        :param inital_value: intial field values, defaults to 0
        """
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT
        self.field: List[list] = [x[:] for x in [[inital_value] * self.x] * self.y]


class Particle():
    """
    single particle in the simulation
    """
    # rather than setting the impact check and having to reset it, toggle parity and
    # impact_check == impact_parity gives you the check status
    impact_parity: bool = True
    count = 0

    def __init__(self, x: float, y: float, delta_x: float, delta_y: float):
        self.name = 'particle' + str(Particle.count)
        Particle.count += 1
        self.position = Vector2d(x, y)
        self.velocity = Vector2d(delta_x, delta_y)
        self.impact_check: bool = not Particle.impact_parity
        self.impact_velocity: Vector2d = None
        self.size = PARTICLE_RADIUS
        self.mass = PARTICLE_MASS

    @staticmethod
    def generate() -> 'Particle':
        """
        generates a new particle with random location and velocity

        :return: new particle
        """
        return Particle(
            random.randrange(PARTICLE_RADIUS, SCREEN_WIDTH - PARTICLE_RADIUS),
            random.randrange(PARTICLE_RADIUS, SCREEN_HEIGHT - PARTICLE_RADIUS),
            random.randrange(-PARTICLE_MAX_SPEED, PARTICLE_MAX_SPEED)/10.0,
            random.randrange(-PARTICLE_MAX_SPEED, PARTICLE_MAX_SPEED)/10.0)
        # return Particle(50, 50, 5, 0)

    def checked(self) -> bool:
        """
        determines if particle has already been checked for impacts

        :return: [description]
        """
        return self.impact_check == Particle.impact_parity

    def update_location(self) -> None:
        """
        updates particle's location
        """
        self.position += self.velocity


class ImpactHelper:

    @staticmethod
    def point_distance(point_a: 'Vector2d', point_b: 'Vector2d') -> float:
        delta = point_a - point_b
        return round(math.sqrt((delta.x)**2 + (delta.y)**2))

    @staticmethod
    def particle_distance(particle_1: 'Particle', particle_2: 'Particle') -> float:
        return ImpactHelper.point_distance(particle_1.position, particle_2.position)

    @staticmethod
    def is_particle_impact(particle_1: Particle, particle_2: Particle) -> bool:
        return ImpactHelper.particle_distance(particle_1, particle_2) <= particle_1.size + particle_2.size

    @staticmethod
    def particle_impact_transformation(particle_1: Particle, particle_2: Particle):
        impact_angle = (particle_1.velocity - particle_2.velocity).to_polar().phi
        velocity_a = particle_1.velocity.rotation_transform(impact_angle)
        velocity_b = particle_2.velocity.rotation_transform(impact_angle)
        return velocity_a, velocity_b, impact_angle

    @staticmethod
    def particle_impact_energy(particle_1: Particle, velocity_1: Vector2d, particle_2: Particle, velocity_2: Vector2d, impact_angle: float):
        m1 = particle_1.mass
        m2 = particle_2.mass
        # print('angle', particle_1.name, impact_angle)
        impact_velocity_1 = Vector2d((m1 - m2)/(m1 + m2) * velocity_1.x + 2 * m2/(m1 + m2) * velocity_2.x, velocity_1.y)
        impact_velocity_2 = Vector2d(2 * m2/(m1 + m2) * velocity_1.x - (m1 - m2)/(m1 + m2) * velocity_2.x, velocity_2.y)
        # print(particle_1.name, particle_1.impact_velocity, impact_velocity_1)
        # print(particle_1.name, particle_2.impact_velocity, impact_velocity_2)

        particle_1.impact_velocity += impact_velocity_1.rotation_transform(-impact_angle)
        particle_2.impact_velocity += impact_velocity_2.rotation_transform(-impact_angle)


class Orbit(arcade.Window):
    def __init__(self):
        self.particle_list = []
        self.field = GravitationalField()
        self.frametime_plotter = FrametimePlotter()
        return super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

    def particle_impact(self, particle_1):
        particle_1.impact_check = Particle.impact_parity

        if particle_1.position.x < particle_1.size or particle_1.position.x > SCREEN_WIDTH - particle_1.size:
            particle_1.impact_velocity = Vector2d(-1 * particle_1.velocity.x, particle_1.velocity.y)

        if particle_1.position.y < particle_1.size or particle_1.position.y > SCREEN_HEIGHT - particle_1.size:
            particle_1.impact_velocity = Vector2d(particle_1.velocity.x, -1 * particle_1.velocity.y)

        particle_2: Particle = None
        for particle_2 in self.particle_list:
            if not particle_2.checked() and ImpactHelper.is_particle_impact(particle_1, particle_2):
                # print('\n\n', particle_2.impact_check, particle_2.impact_parity)
                particle_1.impact_velocity = Vector2d(0, 0)
                particle_2.impact_velocity = Vector2d(0, 0)
                velocity_1, velocity_2, impact_angle = ImpactHelper.particle_impact_transformation(particle_1, particle_2)
                ImpactHelper.particle_impact_energy(particle_1, velocity_1, particle_2, velocity_2, impact_angle)
                # print('impact1', particle_1.name, particle_1.position, particle_1.velocity, particle_1.impact_velocity)
                # print('impact2', particle_1.name, particle_2.position, particle_2.velocity, particle_2.impact_velocity)

        if particle_1.impact_velocity is not None:
            particle_1.velocity.x = particle_1.impact_velocity.x
            particle_1.velocity.y = particle_1.impact_velocity.y
            # print('impact after', particle_1.name, particle_1.position, particle_1.velocity, particle_1.impact_velocity)
            particle_1.update_location()

        particle_1.impact_velocity = None

    def update_field(self):
        pass

    def on_update(self, delta_time):
        # print('......................')
        for particle in self.particle_list:
            particle.update_location()
            self.particle_impact(particle)

        Particle.impact_parity = not Particle.impact_parity

    def on_draw(self):
        arcade.start_render()

        for particle in self.particle_list:
            arcade.draw_circle_filled(round(particle.position.x), round(particle.position.y), particle.size, arcade.color.ANTIQUE_WHITE)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.SPACE:
            self.particle_list.append(Particle.generate())
            self.frametime_plotter.add_event('new particle')


if __name__ == "__main__":
    game = Orbit()
    game.set_update_rate(1/80)
    arcade.run()
    game.frametime_plotter.show()
