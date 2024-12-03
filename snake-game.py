import random
import time
import os

# Set up the game board
width = 20
height = 15

# Initialize the snake
snake = [(width // 2, height // 2)]
direction = 'right'

# Create the food
food = (random.randint(0, width - 1), random.randint(0, height - 1))

# Game loop
while True:
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Get user input
    try:
        new_direction = input('Enter direction (up, down, left, right): ').lower()
        if new_direction in ['up', 'down', 'left', 'right']:
            direction = new_direction
    except KeyboardInterrupt:
        break

    # Move the snake
    head_x, head_y = snake[0]
    if direction == 'up':
        new_head = (head_x, head_y - 1)
    elif direction == 'down':
        new_head = (head_x, head_y + 1)
    elif direction == 'left':
        new_head = (head_x - 1, head_y)
    elif direction == 'right':
        new_head = (head_x + 1, head_y)

    # Check for collisions
    if (new_head[0] < 0 or new_head[0] >= width or
            new_head[1] < 0 or new_head[1] >= height or
            new_head in snake):
        print('Game Over!')
        break

    # Add the new head
    snake.insert(0, new_head)

    # Check for food
    if new_head == food:
        # Create new food
        food = (random.randint(0, width - 1), random.randint(0, height - 1))
    else:
        # Remove the tail
        snake.pop()

    # Draw the game board
    for y in range(height):
        for x in range(width):
            if (x, y) == food:
                print('@', end='')
            elif (x, y) in snake:
                print('#', end='')
            else:
                print('.', end='')
        print()

    # Wait
    time.sleep(0.2)