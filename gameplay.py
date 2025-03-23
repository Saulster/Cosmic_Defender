import pygame
import random
import math
import sys  # Import sys for exiting

# Initialize Pygame
pygame.init()
# pygame.mixer.init()  # Remove sound initialization

# Screen dimensions
WIDTH, HEIGHT = 800, 600
# Use pygame.FULLSCREEN to start in full-screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Cosmic Defender")
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
print(f"Screen Width: {SCREEN_WIDTH}, Screen Height: {SCREEN_HEIGHT}")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)  # For pause screen

# Load assets (replace with your actual file paths)
try:
    player_img = pygame.image.load('spaceship.png').convert_alpha()
    enemy_img = pygame.image.load('enemy.png').convert_alpha()
    bullet_img = pygame.image.load('bullet.png').convert_alpha()
    powerup_img = pygame.image.load('powerup.png').convert_alpha()  # Load powerup image
    powerup_img = pygame.transform.scale(powerup_img, (30, 30))
    # explosion_anim = [pygame.image.load(f'explosion_{i}.png').convert_alpha() for i in range(9)] # Example of explosion frames
    # Load sound effects
    # pygame.mixer.music.load('background_music.wav')  # Replace with your music file #remove
    # shoot_sound = pygame.mixer.Sound('shoot.wav')  # Replace with your sound file #remove
    # explosion_sound = pygame.mixer.Sound('explosion.wav')  # Replace #remove
except FileNotFoundError as e:
    print(
        f"Error loading files: {e}.  Make sure the files exist and are in the correct directory."
    )
    # Handle the error, e.g., provide placeholder images or exit.
    pygame.quit()
    sys.exit()  # Use sys.exit() to exit

# Scale images
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
# explosion_anim = [pygame.transform.scale(img, (50, 50)) for img in explosion_anim]

# Player spaceship
player_x = SCREEN_WIDTH // 2 - 25
player_y = SCREEN_HEIGHT - 100
player_x_change = 0

# Enemy spaceship
enemies = []
num_enemies = 5


def spawn_enemy():
    enemy_x = random.randint(0, SCREEN_WIDTH - 40)
    enemy_y = random.randint(50, 150)
    enemy_x_change = random.choice([-2, 2])  # Random horizontal direction
    enemies.append([enemy_x, enemy_y, enemy_x_change, True])  # Added a boolean to check if enemy is alive


for _ in range(num_enemies):
    spawn_enemy()

# Bullet
bullet_x = 0
bullet_y = SCREEN_HEIGHT - 100
bullet_y_change = -10  # Increased bullet speed
bullet_state = "ready"  # ready - you can't see the bullet, fire - bullet is moving
rapid_fire = False
rapid_fire_duration = 5000  # 5 seconds
rapid_fire_start_time = 0
powerup_x = random.randint(0, SCREEN_WIDTH - 30)
powerup_y = random.randint(50, SCREEN_HEIGHT - 300)
powerup_active = False  # Start with powerup inactive
POWERUP_SIZE = 30
powerup_move = False  # Add this line
last_score = 0  # Add this line
enemy_speed = 2 #added enemy speed
bullets = [] #list of bullets

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
text_x = 10
text_y = 10

# Game Over
game_over_font = pygame.font.Font('freesansbold.ttf', 64)
restart_font = pygame.font.Font('freesansbold.ttf', 20)  # For the restart message

# Starfield
stars = []
for _ in range(200):  # More stars for better effect
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    speed = random.randint(1, 3)  # Varying speeds for depth
    stars.append([x, y, speed])


# Explosion
# explosions = [] # List of explosions.  Each explosion is a list [x, y, frame_index]


def show_score(x, y):
    score = font.render(f"Score: {score_value}", True, WHITE)
    screen.blit(score, (x, y))


def game_over_text():
    game_over = game_over_font.render("GAME OVER", True, RED)
    screen.blit(game_over, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    restart_text = restart_font.render("Press SPACE to Restart", True, WHITE)  # Tell user how to restart
    screen.blit(
        restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)
    )



def player(x, y):
    screen.blit(player_img, (x, y))


def enemy(x, y, is_alive):  # Added is_alive parameter
    if is_alive:
        screen.blit(enemy_img, (x, y))  # Only draw if alive



def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    #screen.blit(bullet_img, (x + 20, y)) #removed

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(
        math.pow(enemy_x - bullet_x, 2) + math.pow(enemy_y - bullet_y, 2)
    )
    if distance < 27:
        return True
    else:
        return False

def is_powerup_collision(player_x, player_y, powerup_x, powerup_y):
    distance = math.sqrt(
        math.pow(player_x - powerup_x, 2) + math.pow(player_y - powerup_y, 2)
    )
    if distance < 30:  # Adjust as needed
        return True
    else:
        return False


# def create_explosion(x, y):
#     explosions.append([x, y, 0]) # Start at frame 0


# Game loop
running = True
game_over = False  # Added game_over state variable
# pygame.mixer.music.play(-1)  # Start background music, -1 for infinite loop #remove
clock = pygame.time.Clock()
paused = False
last_shot_time = 0  # To control rapid fire
bullet_spawn_time = 0


# --- Pause Screen Functions (moved to separate file) ---
def pause_screen():
    """Displays the pause screen and handles user input."""
    global paused, running, game_over, enemies, score_value, player_x, player_y, bullet_y, bullet_state

    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with 50% alpha
    screen.blit(overlay, (0, 0))

    # Pause screen title
    pause_font = pygame.font.Font('freesansbold.ttf', 64)
    pause_text = pause_font.render("Paused", True, WHITE)
    text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(pause_text, text_rect)

    # Button positions and sizes
    button_width = 200
    button_height = 50
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    resume_button_y = SCREEN_HEIGHT // 2 - button_height
    restart_button_y = SCREEN_HEIGHT // 2
    quit_button_y = SCREEN_HEIGHT // 2 + button_height

    # Create buttons
    resume_button = pygame.Rect(button_x, resume_button_y, button_width, button_height)
    restart_button = pygame.Rect(button_x, restart_button_y, button_width, button_height)
    quit_button = pygame.Rect(button_x, quit_button_y, button_width, button_height)

    # Draw buttons
    pygame.draw.rect(screen, GREEN, resume_button)
    pygame.draw.rect(screen, YELLOW, restart_button)
    pygame.draw.rect(screen, RED, quit_button)

    # Button text
    button_font = pygame.font.Font('freesansbold.ttf', 32)
    resume_text = button_font.render("Resume", True, BLACK)
    restart_text = button_font.render("Restart", True, BLACK)
    quit_text = button_font.render("Quit", True, BLACK)

    # Center the text on the buttons
    resume_text_rect = resume_text.get_rect(center=resume_button.center)
    restart_text_rect = restart_text.get_rect(center=restart_button.center)
    quit_text_rect = quit_text.get_rect(center=quit_button.center)

    # Draw the text on the buttons
    screen.blit(resume_text, resume_text_rect)
    screen.blit(restart_text, restart_text_rect)
    screen.blit(quit_text, quit_text_rect)

    pygame.display.update()

    # Handle button clicks
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if resume_button.collidepoint(mouse_pos):
                    paused = False  # Resume the game
                elif restart_button.collidepoint(mouse_pos):
                    # Restart the game
                    game_over = False
                    score_value = 0
                    enemies = []
                    for _ in range(num_enemies):
                        spawn_enemy()
                    player_x = SCREEN_WIDTH // 2 - 25
                    player_y = SCREEN_HEIGHT - 100
                    bullet_y = SCREEN_HEIGHT - 100
                    bullet_state = "ready"
                    paused = False
                    # pygame.mixer.music.play(-1) #remove
                elif quit_button.collidepoint(mouse_pos):
                    running = False
                    paused = False
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False

# --- Main Game Loop ---
while running:
    if not paused:
        screen.fill(BLACK)

        # Draw starfield
        for i, star in enumerate(stars):
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), 2)
            star[1] += star[2]  # Move the star
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -3
                if event.key == pygame.K_RIGHT:
                    player_x_change = 3
                if event.key == pygame.K_SPACE:
                    if not game_over:  # Only allow shooting if game is not over
                        if bullet_state == "ready" or rapid_fire:
                            current_time = pygame.time.get_ticks()
                            if current_time - last_shot_time >= 200 or rapid_fire:  # Control fire rate
                                bullet_x = player_x
                                fire_bullet(bullet_x, bullet_y)
                                # shoot_sound.play() #remove
                                last_shot_time = current_time
                                if rapid_fire:
                                    bullet_spawn_time = pygame.time.get_ticks() #reset

                elif event.key == pygame.K_ESCAPE:
                    paused = True  # Pause the game
                    # pygame.mixer.music.pause() #remove

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player_x_change = 0

        if not game_over:
            # Player movement
            player_x += player_x_change
            if player_x <= 0:
                player_x = 0
            elif player_x >= SCREEN_WIDTH - 50:
                player_x = SCREEN_WIDTH - 50

            # Enemy movement
            for i, enemy_data in enumerate(enemies):
                enemy_data[0] += enemy_data[2]
                if enemy_data[0] <= 0:
                    enemy_data[2] = 2
                    enemy_data[1] += 40
                elif enemy_data[0] >= SCREEN_WIDTH - 40:
                    enemy_data[2] = -2
                    enemy_data[1] += 40

                # Game Over
                if enemy_data[1] > SCREEN_HEIGHT - 200:
                    game_over = True
                    # pygame.mixer.music.stop() #remove
                    break

                # Collision
                collision = is_collision(
                    enemy_data[0], enemy_data[1], bullet_x, bullet_y
                )
                if collision and enemy_data[3]:  # Only collide if enemy is alive
                    bullet_y = SCREEN_HEIGHT - 100
                    bullet_state = "ready"
                    score_value += 1
                    # create_explosion(enemy_data[0], enemy_data[1])
                    # explosion_sound.play() #remove
                    enemy_data[3] = False  # Mark enemy as dead.
                    # enemies.pop(i) # Remove enemy.  This can cause index errors if not done carefully.
                    spawn_enemy()  # Respawn a new enemy.

                enemy(enemy_data[0], enemy_data[1], enemy_data[3])  # Pass the alive state

            # Bullet movement
            if bullet_y <= 0:
                bullet_y = SCREEN_HEIGHT - 100
                bullet_state = "ready"

            if bullet_state == "fire":
                fire_bullet(bullet_x, bullet_y)
                bullet_y += bullet_y_change
                bullets.append([bullet_x+20, bullet_y])

            #draw bullets
            for bullet in bullets:
                screen.blit(bullet_img, (bullet[0], bullet[1]))
                bullet[1] += bullet_y_change
                if bullet[1] < 0:
                    bullets.pop(0)

            # Powerup
            if score_value - last_score >= 10:  # Check if score increased by 10
                powerup_active = True
                powerup_move = True
                last_score = score_value  # Update last_score
                powerup_x = random.randint(0, SCREEN_WIDTH - 30)
                powerup_y = random.randint(50, SCREEN_HEIGHT - 300)

            if powerup_active:
                screen.blit(powerup_img, (powerup_x, powerup_y))  # Draw powerup

                if powerup_move:
                    # Move powerup towards player
                    direction_x = player_x - powerup_x
                    direction_y = player_y - powerup_y
                    distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
                    if distance > 0:
                        powerup_x += (direction_x / distance) * enemy_speed
                        powerup_y += (direction_y / distance) * enemy_speed

                if is_powerup_collision(player_x, player_y, powerup_x, powerup_y):
                    rapid_fire = True
                    rapid_fire_start_time = pygame.time.get_ticks()
                    powerup_active = False # Remove powerup after collision
                    powerup_move = False


            # Check for rapid fire duration
            if rapid_fire:
                if pygame.time.get_ticks() - rapid_fire_start_time >= rapid_fire_duration:
                    rapid_fire = False
                    bullet_spawn_time = 0


            #fire bullets during rapid fire
            if rapid_fire:
                current_time = pygame.time.get_ticks()
                if current_time - bullet_spawn_time >= 100:  # Adjust for desired rapid fire rate
                    bullet_x = player_x
                    fire_bullet(bullet_x, player_y)
                    bullets.append([bullet_x+20, player_y])
                    bullet_spawn_time = current_time



            player(player_x, player_y)
            show_score(text_x, text_y)

            # # Draw explosions
            # for i, explosion in enumerate(explosions):
            #     screen.blit(explosion_anim[explosion[2]], (explosion[0], explosion[1]))
            #     explosion[2] += 1
            #     if explosion[2] >= len(explosion_anim):
            #         explosions.pop(i)
        else:
            game_over_text()
            # pygame.mixer.music.stop() #remove

        pygame.display.update()
        clock.tick(60)
    else:
        pause_screen()

pygame.quit()
sys.exit()
