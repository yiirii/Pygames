import pygame
import random

class Snowfall:
    def __init__(self, screen, num_flakes=100):
        self.screen = screen
        self.num_flakes = num_flakes
        self.snowflakes = []
        self.width, self.height = self.screen.get_size()

        for _ in range(self.num_flakes):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(1, 3)
            speed = random.uniform(1, 3)
            drift = random.uniform(-0.5, 0.5)
            alpha = random.randint(180, 255)
            self.snowflakes.append([x, y, radius, speed, drift, alpha])

        # Create a semi-transparent surface for snow
        self.snow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def update(self):
        for flake in self.snowflakes:
            flake[0] += flake[4]   # horizontal drift
            flake[1] += flake[3]   # fall speed

            # Respawn flake at top when it falls off-screen
            if flake[1] > self.height:
                flake[0] = random.randint(0, self.width)
                flake[1] = random.randint(-10, -1)
                flake[4] = random.uniform(-0.5, 0.5)

    def draw(self):
        self.snow_surface.fill((0, 0, 0, 0))  # Clear transparent layer
        for flake in self.snowflakes:
            pygame.draw.circle(self.snow_surface, (255, 255, 255, flake[5]), (int(flake[0]), int(flake[1])), flake[2])
        self.screen.blit(self.snow_surface, (0, 0))
