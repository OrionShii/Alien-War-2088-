import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 80 

player_level = 0  
player_images = [pygame.image.load(f"spaceship{i}.png") for i in range(5)]
player_images = [pygame.transform.scale(img, (60, 60)) for img in player_images]
player_rect = player_images[player_level].get_rect(center=(player_x, player_y))

bullet_image = pygame.image.load("bullet.png")
bullet_image = pygame.transform.scale(bullet_image, (20, 20))
bullets = []

enemy_ship_image = pygame.image.load("enemy_ship1.png")
enemy_ship_image = pygame.transform.scale(enemy_ship_image, (60, 60))

background_image = pygame.image.load("background.jpg")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.Font(pygame.font.get_default_font(), 36)

shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
level_up_sound = pygame.mixer.Sound("level_up.wav")

shoot_channel = pygame.mixer.Channel(0)
explosion_channel = pygame.mixer.Channel(1)

level = 0  
score = 0
health = 100
exp = 0  
exp_needed = 25  

game_over = False

player_speed = 8  
bullet_speed = 12  
initial_enemy_speed = 3
enemy_speed_increment = 0.5  

max_enemy_speed = 4  
min_enemy_spawn_interval = 30  

initial_enemy_spawn_interval = 120
enemy_spawn_interval_decrement = 5  

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Spaceship War Arcade Game")

def spawn_enemy():
    enemy_x = random.randint(0, SCREEN_WIDTH - enemy_ship_image.get_width())
    enemy_y = random.randint(-200, -50)
    return pygame.Rect(enemy_x, enemy_y, enemy_ship_image.get_width(), enemy_ship_image.get_height())

level_timer = 0
enemy_spawn_timer = 0
enemy_spawn_interval = initial_enemy_spawn_interval  

level_started = False
remove_bullet = False
enemies = [] 

while not game_over:
    screen.fill(BLACK)

    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    keys = pygame.key.get_pressed()

    # Handle player movement (allow backward movement)
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
        player_rect.x += player_speed

    # Shooting bullets
    if keys[pygame.K_SPACE]:
        bullet_x = player_rect.centerx - bullet_image.get_width() // 2
        bullet_y = player_rect.top
        bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_image.get_width(), bullet_image.get_height()))
        shoot_channel.play(shoot_sound)

    # Move bullets
    bullets = [bullet for bullet in bullets if bullet.y > 0]
    for bullet in bullets:
        bullet.y -= bullet_speed

    # Move enemies and check for collisions
    for enemy in enemies:
        dx = player_rect.centerx - enemy.centerx
        dy = player_rect.centery - enemy.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance != 0:
            enemy.x += (dx / distance) * (initial_enemy_speed + player_level * enemy_speed_increment)
            enemy.y += (dy / distance) * (initial_enemy_speed + player_level * enemy_speed_increment)

        if player_rect.colliderect(enemy):
            explosion_channel.play(explosion_sound)
            health -= 10
            enemies.remove(enemy)

    # Check for collisions with bullets
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                explosion_channel.play(explosion_sound)
                score += 10
                exp += 5  # Gain 5 experience points for each enemy killed
                remove_bullet = True
                break  # Stop checking for other collisions with the same bullet

        if bullet.y <= 0 or remove_bullet:
            bullets.remove(bullet)
            remove_bullet = False

    if exp >= exp_needed and not level_started:
        exp -= exp_needed
        player_level += 1
        player_level = min(player_level, 4)
        player_images = [pygame.image.load(f"spaceship{i}.png") for i in range(player_level + 1)]
        player_images = [pygame.transform.scale(img, (60, 60)) for img in player_images]
        player_rect = player_images[player_level].get_rect(center=player_rect.center)
        level_up_sound.play()
        level_started = False

        # Adjust the speed increment based on level
        enemy_speed_increment = 0.5 + player_level * 0.2

        # Limit the maximum enemy speed
        initial_enemy_speed = min(initial_enemy_speed + player_level * enemy_speed_increment, max_enemy_speed)

        # Adjust the enemy spawn interval
        enemy_spawn_interval = max(min_enemy_spawn_interval, enemy_spawn_interval - enemy_spawn_interval_decrement)

        # Increase the number of enemies spawned when leveling up
        max_enemies = min(player_level + 1, 5)
        enemy_spawn_interval = initial_enemy_spawn_interval
        enemies += [spawn_enemy() for _ in range(max_enemies)]

    if enemy_spawn_timer % max(1, enemy_spawn_interval) == 0:
        enemies.append(spawn_enemy())


    screen.blit(player_images[player_level], player_rect)

    for enemy in enemies:
        screen.blit(enemy_ship_image, enemy)

    for bullet in bullets:
        screen.blit(bullet_image, bullet)

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {player_level}", True, WHITE)
    health_text = font.render(f"Health: {health}%", True, WHITE)
    exp_text = font.render(f"Exp: {exp}/{exp_needed}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
    pygame.draw.rect(screen, (255, 0, 0), (10, 50, health * 2, 30))
    screen.blit(exp_text, (10, 90))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

    # Increment timers
    level_timer += 1
    enemy_spawn_timer += 1

    # Check for game over
    if health <= 0:
        game_over = True

# Game over screen
screen.fill(BLACK)
game_over_text = font.render("Game Over", True, WHITE)
score_text = font.render(f"Final Score: {score}", True, WHITE)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
pygame.display.flip()

# Wait for a few seconds before closing the game
pygame.time.wait(3000)

# Clean up
pygame.quit()
sys.exit()
