#!/usr/bin/env python3
import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
CELL_SIZE = 40
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

# Colors for puyos
PUYO_COLORS = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0), # Yellow
    (255, 0, 255), # Magenta
    (0, 255, 255)  # Cyan
]
BG_COLOR = (50, 50, 50)
GRID_COLOR = (80, 80, 80)

# Create game screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puyo Puyo Style Game")
clock = pygame.time.Clock()

# Game board grid (None or color)
grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

def draw_grid():
    for row in range(ROWS):
        for col in range(COLUMNS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)
            if grid[row][col]:
                pygame.draw.circle(screen, grid[row][col], rect.center, CELL_SIZE // 2 - 2)

def find_connected(row, col, color, visited):
    to_check = [(row, col)]
    connected = []
    while to_check:
        r, c = to_check.pop()
        if (r, c) in visited:
            continue
        if r < 0 or r >= ROWS or c < 0 or c >= COLUMNS:
            continue
        if grid[r][c] != color:
            continue
        visited.add((r, c))
        connected.append((r, c))
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            to_check.append((r+dr, c+dc))
    return connected

def clear_groups():
    cleared = False
    visited = set()
    for r in range(ROWS):
        for c in range(COLUMNS):
            if grid[r][c] and (r, c) not in visited:
                connected = find_connected(r, c, grid[r][c], visited)
                if len(connected) >= 4:
                    for pos in connected:
                        grid[pos[0]][pos[1]] = None
                    cleared = True
    return cleared

class FallingPuyo:
    def __init__(self):
        self.color = random.choice(PUYO_COLORS)
        self.x = COLUMNS // 2
        self.y = 0
        self.fall_speed = 500   # milliseconds per one cell drop
        self.last_drop = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_drop > self.fall_speed:
            if not self.check_collision(self.x, self.y + 1):
                self.y += 1
            else:
                grid[self.y][self.x] = self.color
                return False
            self.last_drop = now
        return True

    def move(self, dx):
        new_x = self.x + dx
        if new_x < 0 or new_x >= COLUMNS:
            return
        if not self.check_collision(new_x, self.y):
            self.x = new_x

    def check_collision(self, x, y):
        if y >= ROWS:
            return True
        if grid[y][x] is not None:
            return True
        return False

    def draw(self):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(screen, self.color, rect.center, CELL_SIZE // 2 - 2)

def main():
    running = True
    current_puyo = FallingPuyo()
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_puyo.move(-1)
                elif event.key == pygame.K_RIGHT:
                    current_puyo.move(1)
                elif event.key == pygame.K_DOWN:
                    current_puyo.fall_speed = 50

        screen.fill(BG_COLOR)
        draw_grid()
        if not current_puyo.update():
            while clear_groups():
                for col in range(COLUMNS):
                    for row in range(ROWS - 2, -1, -1):
                        if grid[row][col] and grid[row + 1][col] is None:
                            grid[row + 1][col] = grid[row][col]
                            grid[row][col] = None
            current_puyo = FallingPuyo()
        current_puyo.draw()
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
