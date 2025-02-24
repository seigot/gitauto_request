import pygame
import sys
import random

pygame.init()

# Global variables
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
BOARD_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 240, 240),  # I piece - cyan
    (0, 0, 240),    # J piece - blue
    (240, 160, 0),  # L piece - orange
    (240, 240, 0),  # O piece - yellow
    (0, 240, 0),    # S piece - green
    (160, 0, 240),  # T piece - purple
    (240, 0, 0)     # Z piece - red
]

# Tetromino shapes (defined as matrices)
TETROMINOES = {
    'I': [
         [0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]
    ],
    'J': [
         [1,0,0],
         [1,1,1],
         [0,0,0]
    ],
    'L': [
         [0,0,1],
         [1,1,1],
         [0,0,0]
    ],
    'O': [
         [1,1],
         [1,1]
    ],
    'S': [
         [0,1,1],
         [1,1,0],
         [0,0,0]
    ],
    'T': [
         [0,1,0],
         [1,1,1],
         [0,0,0]
    ],
    'Z': [
         [1,1,0],
         [0,1,1],
         [0,0,0]
    ]
}

def rotate(shape):
    """Rotate a shape clockwise"""
    return [list(row) for row in zip(*shape[::-1])]

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = BOARD_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0

def new_tetromino():
    shape_name = random.choice(list(TETROMINOES.keys()))
    shape = [row[:] for row in TETROMINOES[shape_name]]
    color = COLORS[list(TETROMINOES.keys()).index(shape_name)]
    return Tetromino(shape, color)

def create_board():
    board = [[BLACK for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    return board

def valid_space(tetromino, board, adj_x=0, adj_y=0):
    accepted_positions = [[(j, i) for j in range(BOARD_WIDTH) if board[i][j] == BLACK] for i in range(BOARD_HEIGHT)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(tetromino)
    for pos in formatted:
        x, y = pos
        x += adj_x
        y += adj_y
        if (x, y) not in accepted_positions:
            if y > -1:
                return False
    return True

def convert_shape_format(tetromino):
    positions = []
    for i, row in enumerate(tetromino.shape):
        for j, val in enumerate(row):
            if val:
                positions.append((tetromino.x + j, tetromino.y + i))
    return positions

def check_lost(board):
    for j in range(BOARD_WIDTH):
        if board[0][j] != BLACK:
            return True
    return False

def clear_lines(board, locked_positions):
    cleared = 0
    for i in range(len(board)-1, -1, -1):
        row = board[i]
        if BLACK not in row:
            cleared += 1
            del board[i]
            board.insert(0, [BLACK for _ in range(BOARD_WIDTH)])
    return cleared

# Particle effects for line clear
particles = []

def create_particles(x, y):
    for _ in range(20):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), random.randint(20, 40)])

def update_particles(screen):
    for particle in particles[:]:
        particle[0] += particle[2]
        particle[1] += particle[3]
        particle[4] -= 1
        if particle[4] > 0:
            pygame.draw.circle(screen, WHITE, (int(particle[0]), int(particle[1])), 2)
        else:
            particles.remove(particle)

def draw_board(screen, board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            pygame.draw.rect(screen, board[i][j], (j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for i in range(len(board)+1):
        pygame.draw.line(screen, GRAY, (0, i*BLOCK_SIZE), (SCREEN_WIDTH, i*BLOCK_SIZE))
    for j in range(len(board[0])+1):
        pygame.draw.line(screen, GRAY, (j*BLOCK_SIZE, 0), (j*BLOCK_SIZE, SCREEN_HEIGHT))

def draw_tetromino(screen, tetromino):
    positions = convert_shape_format(tetromino)
    for pos in positions:
        x, y = pos
        pygame.draw.rect(screen, tetromino.color, (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    board = create_board()
    current_piece = new_tetromino()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run:
        fall_time += clock.get_rawtime() / 1000
        clock.tick(FPS)

        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, board) and current_piece.y > 0:
                current_piece.y -= 1
                positions = convert_shape_format(current_piece)
                for pos in positions:
                    x, y = pos
                    if y > -1:
                        board[y][x] = current_piece.color
                cleared = clear_lines(board, {})
                if cleared > 0:
                    for _ in range(cleared):
                        create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                    score += cleared * 100
                current_piece = new_tetromino()
                if not valid_space(current_piece, board):
                    run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, board):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, board):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, board):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.shape = rotate(current_piece.shape)
                    if not valid_space(current_piece, board):
                        for _ in range(3):
                            current_piece.shape = rotate(current_piece.shape)

        screen.fill(BLACK)
        draw_board(screen, board)
        draw_tetromino(screen, current_piece)
        update_particles(screen)

        score_text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
