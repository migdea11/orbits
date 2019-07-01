import math

from lib.helper_types import Vector2d
from lib.particle import Particle

IMPACT_OVERLAP_TOLERANCE = 0.1


def point_distance(point_a: Vector2d, point_b: Vector2d) -> float:
    delta = point_a - point_b
    return round(math.sqrt((delta.x)**2 + (delta.y)**2))


def particle_distance(particle_1: Particle, particle_2: Particle) -> float:
    return point_distance(particle_1.particle_position, particle_2.particle_position)


def is_particle_impact(particle_1: Particle, particle_2: Particle) -> bool:
    return particle_distance(particle_1, particle_2) <= particle_1.size + particle_2.size


def remove_overlap(particle_1: Particle, particle_2: Particle) -> None:
    if ((particle_1.size + particle_2.size) - (particle_distance(particle_1, particle_2)))/2 <= IMPACT_OVERLAP_TOLERANCE:
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


def particle_impact_transformation(particle_1: Particle, particle_2: Particle):
    impact_angle = (particle_1.particle_velocity - particle_2.particle_velocity).to_polar().phi
    velocity_a = particle_1.particle_velocity.rotation_transform(impact_angle)
    velocity_b = particle_2.particle_velocity.rotation_transform(impact_angle)
    return velocity_a, velocity_b, impact_angle


def particle_impact_energy(particle_1: Particle, velocity_1: Vector2d, particle_2: Particle, velocity_2: Vector2d, impact_angle: float):
    m1 = particle_1.mass
    m2 = particle_2.mass

    impact_velocity_1 = Vector2d((m1 - m2)/(m1 + m2) * velocity_1.x + 2 * m2/(m1 + m2) * velocity_2.x, velocity_1.y)
    impact_velocity_2 = Vector2d(2 * m2/(m1 + m2) * velocity_1.x - (m1 - m2)/(m1 + m2) * velocity_2.x, velocity_2.y)

    particle_1.impact_velocity += impact_velocity_1.rotation_transform(-impact_angle)
    particle_2.impact_velocity += impact_velocity_2.rotation_transform(-impact_angle)
