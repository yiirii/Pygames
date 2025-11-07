import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Create a window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Load Background Example")

# Fix the path (remove the leading # and escape properly)
image_path = os.path.join("..", "graphics", "backgrounds", "forest.png")

# Load the image
background = pygame.image.load(image_path).convert()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
