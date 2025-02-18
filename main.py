from dataclasses import asdict

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