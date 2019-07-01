import arcade
from pathlib import Path

from lib.helper_types import Vector2d

PARTICLE_FILE = Path('./images/asteroid-icon.png')
PARTICLE_SCALING = 1.0 / 70
PARTICLE_MAX_SPEED: int = 5  # divide by 10
PARTICLE_RADIUS: int = 7
PARTICLE_MASS: int = 10


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
