import pygame
import random
import sys
from collections import deque

pygame.init()

# Configurations
CELL_SIZE = 40
COLS = 6
ROWS = 12
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puyo Puyo Effect")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]

# Grid (None means empty)
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

# Falling piece (2 blocks in vertical orientation)
def new_piece():
    color = random.choice(colors)
    piece = {'blocks': [(0, COLS // 2), (-1, COLS // 2)], 'color': color}
    return piece

falling_piece = new_piece()

# Particle effect list
particles = []
def create_particles(x, y, color):
    for _ in range(20):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), random.randint(20, 40), color])

def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)

def draw_particles(surface):
    for p in particles:
        x, y, vx, vy, life, color = p
        pygame.draw.circle(surface, color, (int(x), int(y)), 3)

# Check if a cell is valid and empty
def valid_cell(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS and grid[r][c] is None

# Lock falling piece into grid
def lock_piece(piece):
    for (r, c) in piece['blocks']:
        if 0 <= r < ROWS:
            grid[r][c] = piece['color']

# Check for groups of 4 or more adjacent same-color
def find_groups():
    visited = [[False] * COLS for _ in range(ROWS)]
    groups = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is not None and not visited[r][c]:
                color = grid[r][c]
                group = []
                queue = deque()
                queue.append((r, c))
                visited[r][c] = True
                while queue:
                    cr, cc = queue.popleft()
                    group.append((cr, cc))
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                if len(group) >= 4:
                    groups.append((group, color))
    return groups

# Clear groups and apply particle effect
def clear_groups(groups):
    for group, color in groups:
        for (r, c) in group:
            grid[r][c] = None
            cx = c * CELL_SIZE + CELL_SIZE // 2
            cy = r * CELL_SIZE + CELL_SIZE // 2
            create_particles(cx, cy, color)

# Apply gravity
def apply_gravity():
    for c in range(COLS):
        for r in range(ROWS - 2, -1, -1):
            if grid[r][c] is not None:
                nr = r
                while nr + 1 < ROWS and grid[nr + 1][c] is None:
                    grid[nr + 1][c] = grid[nr][c]
                    grid[nr][c] = None
                    nr += 1

# Game loop variables
fall_time = 0
fall_speed = 500  # milliseconds per block fall

while True:
    dt = clock.tick(FPS)
    fall_time += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if len(falling_piece['blocks']) == 2:
                    r0, c0 = falling_piece['blocks'][0]
                    r1, c1 = falling_piece['blocks'][1]
                    if r0 != r1:
                        new_pos = (r0, c0 + 1)
                        if valid_cell(r0, c0 + 1):
                            falling_piece['blocks'][1] = new_pos
                    else:
                        new_pos = (r0 - 1, c0)
                        if valid_cell(r0 - 1, c0):
                            falling_piece['blocks'][1] = new_pos
            elif event.key == pygame.K_LEFT:
                can_move = True
                for (r, c) in falling_piece['blocks']:
                    if not valid_cell(r, c - 1):
                        can_move = False
                        break
                if can_move:
                    falling_piece['blocks'] = [(r, c - 1) for (r, c) in falling_piece['blocks']]
            elif event.key == pygame.K_RIGHT:
                can_move = True
                for (r, c) in falling_piece['blocks']:
                    if not valid_cell(r, c + 1):
                        can_move = False
                        break
                if can_move:
                    falling_piece['blocks'] = [(r, c + 1) for (r, c) in falling_piece['blocks']]

    if fall_time >= fall_speed:
        fall_time = 0
        can_move_down = True
        for (r, c) in falling_piece['blocks']:
            if r + 1 >= ROWS or grid[r + 1][c] is not None:
                can_move_down = False
                break
        if can_move_down:
            falling_piece['blocks'] = [(r + 1, c) for (r, c) in falling_piece['blocks']]
        else:
            lock_piece(falling_piece)
            groups = find_groups()
            if groups:
                clear_groups(groups)
                apply_gravity()
            falling_piece = new_piece()

    screen.fill(BLACK)
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is not None:
                pygame.draw.rect(screen, grid[r][c], (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for (r, c) in falling_piece['blocks']:
        if r >= 0:
            pygame.draw.rect(screen, falling_piece['color'], (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    draw_particles(screen)
    pygame.display.flip()
    update_particles()
