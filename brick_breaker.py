import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
BRICK_ROWS = 5
BRICK_COLUMNS = 10
BRICK_WIDTH = 70
BRICK_HEIGHT = 20
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()

# Paddle
paddle = pygame.Rect((WIDTH - PADDLE_WIDTH) // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_vel = [4, -4]

# Bricks
bricks = []
brick_padding = 5
offset_top = 50
offset_left = (WIDTH - (BRICK_COLUMNS * (BRICK_WIDTH + brick_padding))) // 2

for row in range(BRICK_ROWS):
    brick_row = []
    for col in range(BRICK_COLUMNS):
        brick_x = offset_left + col * (BRICK_WIDTH + brick_padding)
        brick_y = offset_top + row * (BRICK_HEIGHT + brick_padding)
        brick = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
        brick_row.append(brick)
    bricks.append(brick_row)

# Particle effects list
particles = []

def create_particles(x, y):
    for _ in range(20):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), random.randint(20, 40)])

def update_particles():
    for particle in particles[:]:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[4] -= 1
        if particle[4] <= 0:
            particles.remove(particle)

def draw_particles(screen):
    for particle in particles:
        alpha = max(0, int(255 * (particle[4] / 40)))
        color = (YELLOW[0], YELLOW[1], YELLOW[2])
        pygame.draw.circle(screen, color, (int(particle[0]), int(particle[1])), 3)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.x -= 6
    if keys[pygame.K_RIGHT]:
        paddle.x += 6

    if paddle.x < 0:
        paddle.x = 0
    if paddle.x > WIDTH - PADDLE_WIDTH:
        paddle.x = WIDTH - PADDLE_WIDTH

    # Move ball
    ball.x += ball_vel[0]
    ball.y += ball_vel[1]

    # Ball collision with walls
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_vel[0] = -ball_vel[0]
    if ball.top <= 0:
        ball_vel[1] = -ball_vel[1]
    if ball.bottom >= HEIGHT:
        running = False

    # Ball collision with paddle
    if ball.colliderect(paddle) and ball_vel[1] > 0:
        ball_vel[1] = -ball_vel[1]

    # Ball collision with bricks
    for row in bricks:
        for brick in row:
            if ball.colliderect(brick):
                ball_vel[1] = -ball_vel[1]
                create_particles(brick.centerx, brick.centery)
                row.remove(brick)
                break

    update_particles()

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    for row in bricks:
        for brick in row:
            pygame.draw.rect(screen, RED, brick)

    draw_particles(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
