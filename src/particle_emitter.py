import math
from dataclasses import dataclass, fields
from typing import Optional

from src.corefuncs import lerp, clamp

import pygame
from pygame import Vector2, Color
import random
from src.particle_presets import ParticleBaseSettings


def from_kwargs(kwargs):
    return ParticleBaseSettings(**{k: v for k, v in kwargs.items() if k in ParticleBaseSettings.__annotations__})


def interpolate_color(color1, color2, t):
    """
    Interpolates between two Pygame Color objects.

    :param color1: First Pygame Color (e.g., pygame.Color("#be4a2f"))
    :param color2: Second Pygame Color (e.g., pygame.Color("#ead4aa"))
    :param t: Interpolation factor (0.0 to 1.0)
    :return: Interpolated Pygame Color
    """
    return pygame.Color(
        int(color1.r + (color2.r - color1.r) * t),
        int(color1.g + (color2.g - color1.g) * t),
        int(color1.b + (color2.b - color1.b) * t),
        int(color1.a + (color2.a - color1.a) * t)
    )


@dataclass
class Particle:
    position: Vector2
    start_position: Vector2
    velocity: Vector2
    frequency: float
    phase: float
    direction: int
    color: Color
    time_elapsed: float
    lifetime: float
    size: int
    surf: pygame.Surface | None
    gsurf: pygame.Surface | None
    alpha: int


class ParticleEmitter:
    """
    A particle emitter that spawns and manages particles.
    """
    _SURFACES_RECT: list[pygame.Surface] = [
        pygame.Surface((i, i), pygame.SRCALPHA) for i in range(1, 11)
    ]
    _SURFACES_CIRCLE: list[pygame.Surface] = [
        pygame.Surface((i * 2, i * 2), pygame.SRCALPHA) for i in range(1, 11)
    ]

    # Fill rectangle surfaces with white
    for surf in _SURFACES_RECT:
        surf.fill((255, 255, 255, 255))

    # Pre-draw circles onto surfaces
    for i, surf in enumerate(_SURFACES_CIRCLE, start=1):
        pygame.draw.circle(surf, (255, 255, 255, 255), (i, i), i)

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the particle emitter.

        :param kwargs: Optional configuration settings for the emitter.
        """
        self.position = pygame.Vector2(kwargs.get('position', (0, 0)))
        self.size = pygame.Vector2(kwargs.get('size', (0, 0)))
        self.dimensions = pygame.Vector2(64, 64)
        self.particles: list[Particle] = []  # List of active particles
        self.spawn_timer: float = 0  # Timer for spawning new particles
        self.master_clock: float = 0  # Global emitter clock
        self.time_elapsed: float = 0  # Elapsed time since last update
        self.parent: Optional[object] = kwargs.get('parent', False)  # Parent object (if any)
        self.blit_list: list = []  # List of surfaces to be blitted
        self.glow_blit_list: list = []  # List of glow surfaces to be blitted
        self.particle_count: int = 0  # Number of particles spawned
        self.is_active: bool = True  # Whether the emitter is currently active

        self.p_base: ParticleBaseSettings = ParticleBaseSettings()  # Default particle settings

        # Apply configuration settings if provided in kwargs
        self.apply_config(from_kwargs(kwargs))

    @property
    def room_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.position.x // self.dimensions.x * self.dimensions.x,
            self.position.y // self.dimensions.y * self.dimensions.y, self.dimensions.x, self.dimensions.y
        )

    def apply_config(self, config: ParticleBaseSettings) -> None:
        """
        This function is for in engine use only. It will overwrite the existing settings with a new settings
        object.
        :param config:
        :return:
        """
        for f in fields(self.p_base):
            if hasattr(config, f.name):  # Ensure the field exists in the provided config
                setattr(self.p_base, f.name, getattr(config, f.name))
        if isinstance(self.p_base.color_start, str):
            self.p_base.color_start = Color(self.p_base.color_start)
        if isinstance(self.p_base.color_end, str):
            self.p_base.color_end = Color(self.p_base.color_end)

    def spawn_particle_group(self, amount: int) -> None:
        """
        Spawns a group of particles.

        :param amount: The number of particles to spawn.
        """
        for _ in range(amount):
            self.__spawn_particle()

    def set_room_dimensions(self, coords: Vector2):
        self.dimensions = coords

    def __spawn_particle_rate(self, spawn_rate: int) -> None:
        """
        Spawns particles based on a given spawn rate.

        :param spawn_rate: The number of particles to spawn per call.
        """
        for _ in range(spawn_rate):
            self.__spawn_particle()

    def set_state(self, state: bool) -> None:
        """
        Sets the active state of the particle emitter.

        :param state: True to activate, False to deactivate the emitter.
        """
        self.is_active = state

    def __spawn_particle(self) -> None:
        """
        Spawns a single particle with randomized properties.
        """
        rnd_x: float = random.uniform(0, self.size.x)
        rnd_y: float = random.uniform(0, self.size.y)

        pos_x: float = self.position.x + rnd_x
        pos_y: float = self.position.y + rnd_y

        frequency: float = random.uniform(0.3, 0.6)
        phase: float = random.uniform(0.6, 2 * math.pi)
        random_lifetime_deviation: float = 0

        rnd_x_dir: int = random.choice([-1, 1]) if self.p_base.random_x_dir else 1
        rnd_y_dir: int = random.choice([-1, 1]) if self.p_base.random_y_dir else 1
        rnd_x_deviation: float = random.uniform(0, self.p_base.random_velocity_deviation)

        v: Vector2 = Vector2(
            self.p_base.particle_velocity_x * rnd_x_dir + rnd_x_deviation,
            self.p_base.particle_velocity_y * rnd_y_dir
        )

        psurf: Optional[pygame.Surface] = None
        match self.p_base.particle_type:
            case "RECT":
                psurf = self._get_rect_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "CIRCLE":
                psurf = self._get_circle_surface(self.p_base.start_size)
                psurf.fill(self.p_base.color_start)
            case "ANIMATION":
                pass

        particle = Particle(
            position=Vector2(pos_x, pos_y),
            start_position=Vector2(pos_x, pos_y),
            velocity=v,
            frequency=frequency,
            phase=phase,
            direction=1,
            color=self.p_base.color_start,
            time_elapsed=0,
            lifetime=self.p_base.lifetime - random_lifetime_deviation,
            size=self.p_base.start_size,
            surf=psurf,
            alpha=self.p_base.start_alpha,
            gsurf=None
        )

        self.particles.append(particle)
        self.particle_count += 1

    def update(self, dt: float) -> None:
        """
        Updates the particle emitter state.

        :param dt: Delta time since the last update.
        """
        self.time_elapsed += dt
        self.spawn_timer += dt
        self.blit_list.clear()
        self.glow_blit_list.clear()

        if self.is_active:
            match self.p_base.spawn_type:
                case "AUTO":
                    self.__update_auto()
                case "EVENT":
                    self.__update_spawn()

        self.__update_particles(dt)

    def update_position(self, position: Vector2) -> None:
        """
        Updates the emitter's position. Should be called if the emitter is attached to an entity.

        :param position: The new position of the emitter.
        """
        self.position = position

    def _get_rect_surface(self, size: int) -> pygame.Surface:
        """
        Retrieves a rectangle surface of the given size.

        :param size: The size of the rectangle surface.
        :return: A copy of the requested rectangle surface.
        :raises ValueError: If the size is out of the allowed range (1-10).
        """
        if 0 <= size <= 10:
            return self._SURFACES_RECT[size - 1].copy()
        raise ValueError("Size must be between 1 and 10")

    def _get_circle_surface(self, radius: int) -> pygame.Surface:
        """
        Retrieves a circle surface of the given radius.

        :param radius: The radius of the circle surface.
        :return: A copy of the requested circle surface.
        :raises ValueError: If the radius is out of the allowed range (1-10).
        """
        if 1 <= radius <= 10:
            return self._SURFACES_CIRCLE[radius - 1].copy()
        raise ValueError("Radius must be between 1 and 10")

    def __update_auto(self) -> None:
        """
        Updates the emitter when in automatic spawn mode.
        """
        if self.spawn_timer >= self.p_base.spawn_delay:
            if random.randint(0, 100) < self.p_base.particle_chance:
                self.__spawn_particle_rate(self.p_base.spawn_rate)
                self.spawn_timer = 0

    def __update_spawn(self) -> None:
        """
        Placeholder for event-driven particle spawning.
        """
        pass

    def __update_particles(self, dt: float) -> None:
        """
        Updates the active particles.

        :param dt: Delta time since the last update.
        """
        self.particles = [p for p in self.particles if self.room_rect.collidepoint(p.position)]

        for particle in self.particles:
            if self.p_base.sin_x:
                particle.position.x += particle.direction * (
                        (math.sin(self.time_elapsed * particle.frequency + particle.phase) * 1) / 8
                )
            else:
                particle.position.x += particle.velocity.x * dt

            if self.p_base.sin_y:
                particle.position.y += particle.direction * (
                        (math.sin(self.time_elapsed * particle.frequency + particle.phase) * 1) / 8
                )
            else:
                particle.position.y += particle.velocity.y * dt

            min_dt: float = 1 / 240
            _dt: float = max(dt, min_dt)
            particle.time_elapsed += _dt

            try:
                if particle.time_elapsed >= particle.lifetime:
                    self.particles.remove(particle)
            except ValueError as e:
                print(f"{e}: Particle already removed")

            t: float = (particle.time_elapsed / particle.lifetime) ** 2
            particle.color = interpolate_color(particle.color, self.p_base.color_end, t)
            particle.size = lerp(particle.size, self.p_base.end_size, t)
            particle.alpha = lerp(particle.alpha, self.p_base.end_alpha, t)

            psurf: Optional[pygame.Surface] = None
            gsurf: Optional[pygame.Surface] = None

            match self.p_base.particle_type:
                case "RECT":
                    psurf = self._get_rect_surface(clamp(int(particle.size), 1, 10))
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)
                    if self.p_base.glow_size > 0:
                        gsurf = self._get_rect_surface(clamp(
                            int(particle.size + self.p_base.glow_size + random.choice(
                                [self.p_base.random_glow, -self.p_base.random_glow])
                                ), 1, 10))
                        gsurf.fill((
                            int(particle.color.r * (particle.alpha / 255)),
                            int(particle.color.g * (particle.alpha / 255)),
                            int(particle.color.b * (particle.alpha / 255))
                        ))
                case "CIRCLE":
                    psurf = self._get_circle_surface(clamp(int(particle.size), 1, 10))
                    psurf.fill(particle.color)
                    psurf.set_alpha(particle.alpha)
                    if self.p_base.glow_size > 0:
                        gsurf = self._get_circle_surface(clamp(
                            int(particle.size + self.p_base.glow_size + random.choice(
                                [self.p_base.random_glow, -self.p_base.random_glow])
                                ), 1, 10))
                        gsurf.fill((
                            int(particle.color.r * (particle.alpha / 255)),
                            int(particle.color.g * (particle.alpha / 255)),
                            int(particle.color.b * (particle.alpha / 255))
                        ))
                case "ANIMATION":
                    pass

            particle.surf = psurf
            particle.gsurf = gsurf
            self.blit_list.append((psurf, particle.position))

    def render(self, surf: pygame.Surface, offset: tuple[int, int] = (0, 0)) -> None:
        """
        Renders the particles onto the given surface.

        :param surf: The surface to render onto.
        :param offset: The rendering offset.
        """

        if self.p_base.particle_type == 'LINE':
            for p in self.particles:
                velocity_length: float = math.sqrt(p.velocity.x ** 2 + p.velocity.y ** 2)
                direction_x: float = p.velocity.x / velocity_length
                direction_y: float = p.velocity.y / velocity_length
                end_x: float = p.position.x + direction_x * p.size
                end_y: float = p.position.y + direction_y * p.size
                end_p: Vector2 = Vector2(end_x, end_y)
                pygame.draw.aaline(surf, p.color, p.position - offset, end_p - offset)
        else:
            surf.fblits(self.blit_list)

        for p in self.particles:
            if p.gsurf:
                surf.blit(p.gsurf, p.position - offset, special_flags=pygame.BLEND_RGBA_ADD)
