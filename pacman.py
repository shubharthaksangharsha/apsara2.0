import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 600
HEIGHT = 600
PACMAN_SIZE = 50
PACMAN_SPEED = 5

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the clock
clock = pygame.time.Clock()

# Set up the pacman
pacman_x = WIDTH / 2
pacman_y = HEIGHT / 2
pacman_direction = 'right'

# Set up the pellets
pellets = [(random.randint(0, WIDTH - PACMAN_SIZE), random.randint(0, HEIGHT - PACMAN_SIZE)) for _ in range(10)]

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pacman_direction = 'up'
            elif event.key == pygame.K_DOWN:
                pacman_direction = 'down'
            elif event.key == pygame.K_LEFT:
                pacman_direction = 'left'
            elif event.key == pygame.K_RIGHT:
                pacman_direction = 'right'

    # Move the pacman
    if pacman_direction == 'up':
        pacman_y -= PACMAN_SPEED
    elif pacman_direction == 'down':
        pacman_y += PACMAN_SPEED
    elif pacman_direction == 'left':
        pacman_x -= PACMAN_SPEED
    elif pacman_direction == 'right':
        pacman_x += PACMAN_SPEED

    # Keep the pacman on the screen
    if pacman_x < 0:
        pacman_x = 0
    elif pacman_x > WIDTH - PACMAN_SIZE:
        pacman_x = WIDTH - PACMAN_SIZE
    if pacman_y < 0:
        pacman_y = 0
    elif pacman_y > HEIGHT - PACMAN_SIZE:
        pacman_y = HEIGHT - PACMAN_SIZE

    # Draw everything
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 0), (pacman_x, pacman_y, PACMAN_SIZE, PACMAN_SIZE))
    for pellet in pellets:
        pygame.draw.rect(screen, (255, 255, 255), (pellet[0], pellet[1], 10, 10))
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)