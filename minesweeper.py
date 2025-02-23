#!/usr/bin/env python3
import random
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_board(rows, cols, bombs):
    board = [[0 for _ in range(cols)] for _ in range(rows)]
    bomb_positions = set()
    while len(bomb_positions) < bombs:
        r = random.randint(0, rows-1)
        c = random.randint(0, cols-1)
        bomb_positions.add((r, c))
    for r, c in bomb_positions:
        board[r][c] = 'B'
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != 'B':
                    board[nr][nc] += 1
    return board, bomb_positions

def display_board(board, revealed):
    print("    " + " ".join(str(i) for i in range(len(board[0]))))
    for idx, row in enumerate(board):
        line = []
        for jdx, cell in enumerate(row):
            if revealed[idx][jdx]:
                if cell == 0:
                    line.append(" ")
                else:
                    line.append(str(cell))
            else:
                line.append("#")
        print(f"{idx:2d}  " + " ".join(line))

def reveal_cell(board, revealed, row, col):
    if revealed[row][col]:
        return
    revealed[row][col] = True
    if board[row][col] == 0:
        # reveal neighbors
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                    if not revealed[nr][nc]:
                        reveal_cell(board, revealed, nr, nc)

def game():
    rows, cols, bombs = 9, 9, 10
    board, bomb_positions = generate_board(rows, cols, bombs)
    revealed = [[False]*cols for _ in range(rows)]
    while True:
        clear_screen()
        display_board(board, revealed)
        inp = input("Enter row and column (e.g. 0 1): ")
        try:
            row, col = map(int, inp.split())
        except:
            print("Invalid input. Try again.")
            time.sleep(1)
            continue
        if not (0 <= row < rows and 0 <= col < cols):
            print("Invalid coordinates. Try again.")
            time.sleep(1)
            continue
        if (row, col) in bomb_positions:
            clear_screen()
            # fun explosion effect with ascii art
            print("BOOM! You hit a bomb!")
            explosion = [
                "     . . .",
                "   .       .",
                "  .  BOOM!  .",
                "   .       .",
                "     . . ."
            ]
            for line in explosion:
                print(line)
                time.sleep(0.5)
            print("Game Over!")
            break
        else:
            reveal_cell(board, revealed, row, col)
            # Check for win condition
            win = True
            for i in range(rows):
                for j in range(cols):
                    if not revealed[i][j] and board[i][j] != 'B':
                        win = False
                        break
                if not win:
                    break
            if win:
                clear_screen()
                display_board(board, revealed)
                print("Congratulations! You cleared the board!")
                break

if __name__ == "__main__":
    game()
