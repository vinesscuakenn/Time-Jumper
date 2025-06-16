import asyncio
import platform
import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width = 600
height = 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Time Jumper")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
yellow = (255, 255, 0)

# Player properties
player_size = 15
player_x = 50
player_y = height // 2
player_speed = 4

# Time jump properties
time_jump_duration = 2  # Seconds to jump back
time_jump_cooldown = 5  # Seconds before next jump
last_jump_time = 0
player_positions = []  # Store player positions for time jump

# Obstacle and orb properties
obstacle_size = 20
obstacle_speed = 3
orb_size = 10
obstacles = []
orbs = []
spawn_rate = 0.03  # Probability of spawning per frame

# Game variables
score = 0
game_time = 20  # Initial game duration in seconds
start_time = pygame.time.get_ticks() // 1000
running = True

# Function to create a new obstacle
def create_obstacle():
    x = width
    y = random.randint(0, height - obstacle_size)
    return {'x': x, 'y': y}

# Function to create a new orb
def create_orb():
    x = width
    y = random.randint(0, height - orb_size)
    return {'x': x, 'y': y}

# Setup function for initialization
def setup():
    global player_x, player_y, player_positions, obstacles, orbs, score, game_time, start_time, last_jump_time, running
    player_x = 50
    player_y = height // 2
    player_positions = []
    obstacles = []
    orbs = [create_orb() for _ in range(3)]
    score = 0
    game_time = 20
    start_time = pygame.time.get_ticks() // 1000
    last_jump_time = -time_jump_cooldown
    running = True
    window.fill(black)
    pygame.display.update()

# Update loop for game logic
async def update_loop():
    global player_x, player_y, player_positions, obstacles, orbs, score, game_time, last_jump_time, running

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            current_time = pygame.time.get_ticks() // 1000
            if event.key == pygame.K_SPACE and current_time - last_jump_time >= time_jump_cooldown:
                # Perform time jump
                if player_positions:
                    last_position = player_positions[-min(len(player_positions), FPS * time_jump_duration)]
                    player_x, player_y = last_position
                    last_jump_time = current_time

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < height - player_size:
        player_y += player_speed

    # Store player position for time jump
    player_positions.append((player_x, player_y))
    if len(player_positions) > FPS * time_jump_duration:
        player_positions.pop(0)

    # Spawn obstacles and orbs
    if random.random() < spawn_rate:
        obstacles.append(create_obstacle())
    if random.random() < spawn_rate / 2:
        orbs.append(create_orb())

    # Update obstacle positions
    for obstacle in obstacles[:]:
        obstacle['x'] -= obstacle_speed
        if obstacle['x'] < -obstacle_size:
            obstacles.remove(obstacle)

    # Update orb positions
    for orb in orbs[:]:
        orb['x'] -= obstacle_speed / 2
        if orb['x'] < -orb_size:
            orbs.remove(orb)

    # Check collisions
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for obstacle in obstacles[:]:
        obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle_size, obstacle_size)
        if player_rect.colliderect(obstacle_rect):
            return False  # Game over on collision

    for orb in orbs[:]:
        orb_rect = pygame.Rect(orb['x'], orb['y'], orb_size, orb_size)
        if player_rect.colliderect(orb_rect):
            score += 1
            game_time += 2  # Add 2 seconds to game time
            orbs.remove(orb)

    # Check time limit
    current_time = pygame.time.get_ticks() // 1000
    if current_time - start_time >= game_time:
        return False

    # Draw the screen
    window.fill(black)
    pygame.draw.rect(window, white, (player_x, player_y, player_size, player_size))  # Draw player
    for obstacle in obstacles:
        pygame.draw.rect(window, blue, (obstacle['x'], obstacle['y'], obstacle_size, obstacle_size))  # Draw obstacles
    for orb in orbs:
        pygame.draw.circle(window, yellow, (int(orb['x'] + orb_size // 2), int(orb['y'] + orb_size // 2)), orb_size // 2)  # Draw orbs
    pygame.display.set_caption(f"Time Jumper - Score: {score} | Time: {game_time - (current_time - start_time)}")
    pygame.display.update()

    return True

# Main game loop
FPS = 60

async def main():
    setup()
    global running
    while running:
        running = await update_loop()
        await asyncio.sleep(1.0 / FPS)

    # Game over message
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over - Score: {score}", True, white)
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
    pygame.display.update()
    await asyncio.sleep(2)  # Wait 2 seconds
    pygame.quit()

# Run the game based on platform
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
