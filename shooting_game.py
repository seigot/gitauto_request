import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game - Gradius Inspired")
clock = pygame.time.Clock()

# Player settings
player_width, player_height = 50, 30
player = pygame.Rect(50, HEIGHT//2 - player_height//2, player_width, player_height)
player_speed = 5

# Bullet settings
bullets = []
bullet_speed = 10

# Enemy settings
enemies = []
enemy_width, enemy_height = 40, 30
enemy_speed = 3
spawn_enemy_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy_event, 1000)  # spawn enemy every 1 second

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == spawn_enemy_event:
            enemy_y = random.randint(0, HEIGHT - enemy_height)
            enemy = pygame.Rect(WIDTH, enemy_y, enemy_width, enemy_height)
            enemies.append(enemy)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= player_speed
    if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
        player.y += player_speed
    if keys[pygame.K_SPACE]:
        # Add a bullet from the player's position
        bullet = pygame.Rect(player.right, player.centery - 5, 10, 5)
        bullets.append(bullet)

    # Move bullets
    for bullet in bullets[:]:
        bullet.x += bullet_speed
        if bullet.x > WIDTH:
            bullets.remove(bullet)

    # Move enemies
    for enemy in enemies[:]:
        enemy.x -= enemy_speed
        if enemy.right < 0:
            enemies.remove(enemy)

    # Collision detection between bullets and enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # Collision detection between player and enemies
    for enemy in enemies:
        if player.colliderect(enemy):
            running = False

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, player)
    for bullet in bullets:
        pygame.draw.rect(screen, GREEN, bullet)
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
