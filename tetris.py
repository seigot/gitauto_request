#!/usr/bin/env python3
import pygame
import random
import sys

# Global settings
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Shapes definitions: (list of rotations)
SHAPES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1]],
        [[1, 1],
         [1, 0],
         [1, 0]],
        [[1, 1, 1],
         [0, 0, 1]],
        [[0, 1],
         [0, 1],
         [1, 1]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1]],
        [[1, 0],
         [1, 0],
         [1, 1]],
        [[1, 1, 1],
         [1, 0, 0]],
        [[1, 1],
         [0, 1],
         [0, 1]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0]],
        [[1, 0],
         [1, 1],
         [0, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1]],
        [[1, 0],
         [1, 1],
         [1, 0]],
        [[1, 1, 1],
         [0, 1, 0]],
        [[0, 1],
         [1, 1],
         [0, 1]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1]],
        [[0, 1],
         [1, 1],
         [1, 0]]
    ]
}

def rotate(shape):
    """Rotate shape 90 degrees clockwise."""
    return [list(row) for row in zip(*shape[::-1])]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris - Enjoy the Effects!")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0

    def new_piece(self):
        shape_key = random.choice(list(SHAPES.keys()))
        shape = random.choice(SHAPES[shape_key])
        color = [random.randint(50, 255) for _ in range(3)]
        return {'shape': shape, 'x': COLS // 2 - len(shape[0]) // 2, 'y': 0, 'color': color, 'key': shape_key}

    def valid_move(self, piece, adj_x=0, adj_y=0):
        shape = piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = x + piece['x'] + adj_x
                    new_y = y + piece['y'] + adj_y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self, piece):
        shape = piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if piece['y'] + y < 0:
                        self.game_over = True
                    else:
                        self.grid[piece['y'] + y][piece['x'] + x] = piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        for row in self.grid:
            if 0 not in row:
                lines_cleared += 1
                self.show_line_clear_effect(row)
            else:
                new_grid.append(row)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(COLS)])
        self.score += lines_cleared ** 2
        self.grid = new_grid

    def show_line_clear_effect(self, row):
        # Simple effect: flash the line with white color
        effect_surface = pygame.Surface((WIDTH, CELL_SIZE))
        effect_surface.fill(WHITE)
        self.screen.blit(effect_surface, (0, self.grid.index(row) * CELL_SIZE))
        pygame.display.flip()
        pygame.time.delay(100)

    def draw_grid(self):
        self.screen.fill(BLACK)
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        shape = self.current_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = (self.current_piece['x'] + x) * CELL_SIZE
                    py = (self.current_piece['y'] + y) * CELL_SIZE
                    pygame.draw.rect(self.screen, self.current_piece['color'], (px, py, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)
        pygame.display.flip()

    def run(self):
        drop_event = pygame.USEREVENT + 1
        pygame.time.set_timer(drop_event, 500)
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == drop_event:
                    if self.valid_move(self.current_piece, adj_y=1):
                        self.current_piece['y'] += 1
                    else:
                        self.lock_piece(self.current_piece)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.valid_move(self.current_piece, adj_x=-1):
                        self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT and self.valid_move(self.current_piece, adj_x=1):
                        self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN and self.valid_move(self.current_piece, adj_y=1):
                        self.current_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        rotated = rotate(self.current_piece['shape'])
                        temp_piece = self.current_piece.copy()
                        temp_piece['shape'] = rotated
                        if self.valid_move(temp_piece):
                            self.current_piece['shape'] = rotated
            self.draw_grid()
            self.clock.tick(FPS)
        self.game_over_screen()

    def game_over_screen(self):
        font = pygame.font.SysFont("Arial", 36)
        text_surface = font.render("Game Over!", True, WHITE)
        self.screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Tetris()
    game.run()
