import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Defender")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player spaceship
player_img = pygame.image.load('spaceship.png')  # Replace with your image
player_img = pygame.transform.scale(player_img, (50, 50))
player_x = WIDTH // 2 - 25
player_y = HEIGHT - 100
player_x_change = 0

# Enemy spaceship
enemy_img = pygame.image.load('enemy.png')  # Replace with your image
enemy_img = pygame.transform.scale(enemy_img, (40, 40))
enemies = []
num_enemies = 5

for _ in range(num_enemies):
    enemy_x = random.randint(0, WIDTH - 40)
    enemy_y = random.randint(50, 150)
    enemy_x_change = 2
    enemies.append([enemy_x, enemy_y, enemy_x_change])

# Bullet
bullet_img = pygame.image.load('bullet.png')  # Replace with your image
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
bullet_x = 0
bullet_y = HEIGHT - 100
bullet_y_change = -5
bullet_state = "ready"  # ready - you can't see the bullet, fire - bullet is moving

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
text_x = 10
text_y = 10

# Game Over
game_over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render(f"Score: {score_value}", True, WHITE)
    screen.blit(score, (x, y))

def game_over_text():
    game_over = game_over_font.render("GAME OVER", True, RED)
    screen.blit(game_over, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

def player(x, y):
    screen.blit(player_img, (x, y))

def enemy(x, y):
    screen.blit(enemy_img, (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 20, y))

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(math.pow(enemy_x - bullet_x, 2) + math.pow(enemy_y - bullet_y, 2))
    if distance < 27:
        return True
    else:
        return False

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -3
            if event.key == pygame.K_RIGHT:
                player_x_change = 3
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bullet_x = player_x
                    fire_bullet(bullet_x, bullet_y)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    # Player movement
    player_x += player_x_change
    if player_x <= 0:
        player_x = 0
    elif player_x >= WIDTH - 50:
        player_x = WIDTH - 50

    # Enemy movement
    for i, enemy_data in enumerate(enemies):
        enemy_data[0] += enemy_data[2]
        if enemy_data[0] <= 0:
            enemy_data[2] = 2
            enemy_data[1] += 40
        elif enemy_data[0] >= WIDTH - 40:
            enemy_data[2] = -2
            enemy_data[1] += 40

        # Game Over
        if enemy_data[1] > HEIGHT - 200:
            for j in range(num_enemies):
                enemies[j][1] = 2000 # Offscreen
            game_over_text()
            break

        # Collision
        collision = is_collision(enemy_data[0], enemy_data[1], bullet_x, bullet_y)
        if collision:
            bullet_y = HEIGHT - 100
            bullet_state = "ready"
            score_value += 1
            enemy_data[0] = random.randint(0, WIDTH - 40)
            enemy_data[1] = random.randint(50, 150)

        enemy(enemy_data[0], enemy_data[1])

    # Bullet movement
    if bullet_y <= 0:
        bullet_y = HEIGHT - 100
        bullet_state = "ready"

    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y += bullet_y_change

    player(player_x, player_y)
    show_score(text_x, text_y)
    pygame.display.update()
    clock.tick(60) #Limit to 60 frames per second.

pygame.quit()