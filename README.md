# Particle System Library

## Overview

This library provides a flexible and efficient particle system implementation using **Pygame**. It supports various particle effects, including:

- Rectangular and circular particles
- Sinusoidal motion effects
- Color, size, and alpha interpolation over lifetime
- Glow effects
- Particle animations

The **ParticleEmitter** class serves as the core of this system, handling particle spawning, updates, and rendering.

## Installation

Ensure you have **Pygame** installed before using this library:

```sh
pip install pygame-ce
```

## Usage

### Importing the Library

```python
import pygame
from pygame.math import Vector2
from src.particle_emitter import ParticleEmitter
from src.particle_presets import ExampleSettings

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
tick = 60
# Create an emitter at position (400, 300)
emitter = ParticleEmitter(position=(799, 0), size=(4, 600))
emitter.apply_config(ExampleSettings())
emitter.set_room_dimensions(Vector2(800, 600))
```

### Updating and Rendering

```python
running = True
while running:
    dt = clock.tick(tick) / 1000.0  # Delta time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    emitter.update(dt)
    
    screen.fill((0, 0, 0))  # Clear screen
    emitter.render(screen)
    pygame.display.flip()
    pygame.display.set_caption("Particle Demo")

pygame.quit()
```

## Example

![Example Application](data/pyg_example.gif)

## Features

### **Particle Class**

Each particle has:

- **Position & Velocity**: Determines movement.
- **Lifetime**: Automatically removes particles after expiration.
- **Color & Alpha**: Supports interpolation between start and end values.
- **Glow Effect**: Creates a blurred glowing effect around particles.
- **Surface Rendering**: Supports different shapes (rectangles, circles).

### **ParticleEmitter Class**

Manages particle behavior, including:

- **Configurable Particle Settings**: Lifetime, size, color transitions.
- **Sinusoidal Movement**: Allows oscillating motion along X/Y axes.
- **Efficient Rendering**: Uses pre-cached surfaces for performance.
- **Glow Effect Rendering**: Ensures realistic glow application.

## API Reference

### `ParticleEmitter(position: Vector2, parent: Optional[Entity] = None)`

Initializes a particle emitter.

### `spawn_particle_group(amount: int) -> None`

Spawns `amount` particles.

### `set_state(state: bool) -> None`

Activates (`True`) or deactivates (`False`) the emitter.

### `update_position(position: Vector2) -> None`

Moves the emitter to a new position.

### `render(surf: pygame.Surface, offset: Tuple[int, int] = (0, 0)) -> None`

Renders particles onto the given surface.

## Disclaimer

The API is still experimental and subject to change

## License

This library is open-source under the **MIT License**.

## Author

Developed by karat-1.
