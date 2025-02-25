#!/usr/bin/env python3

import random
import time
import os
import sys

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        CYAN = ''
        MAGENTA = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

def clear_screen():
    os.system('cls' if os.name == "nt" else "clear")

class Minesweeper:
    def __init__(self, rows=10, cols=10, bombs=10):
        self.rows = rows
        self.cols = cols
        self.bombs = bombs
        self.board = [[" " for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.place_bombs()
        self.calculate_numbers()

    def place_bombs(self):
        placed = 0
        while placed < self.bombs:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.board[r][c] != "B":
                self.board[r][c] = "B"
                placed += 1

    def calculate_numbers(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == "B":
                    continue
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.board[nr][nc] == "B":
                                count += 1
                self.board[r][c] = str(count) if count > 0 else " "

    def display_board(self):
        clear_screen()
        print(Fore.CYAN + Style.BRIGHT + "   " + " ".join([str(i) for i in range(self.cols)]))
        for i in range(self.rows):
            line = f"{i:2d} "
            for j in range(self.cols):
                if self.revealed[i][j]:
                    if self.board[i][j] == "B":
                        line += Fore.RED + "B " + Style.RESET_ALL
                    else:
                        line += Fore.GREEN + self.board[i][j] + " " + Style.RESET_ALL
                else:
                    line += Fore.YELLOW + "# " + Style.RESET_ALL
            print(line)
        time.sleep(0.5)

    def reveal(self, r, c):
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols or self.revealed[r][c]:
            return
        self.revealed[r][c] = True
        if self.board[r][c] == " ":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        self.reveal(r + dr, c + dc)

    def play(self):
        while not self.game_over:
            self.display_board()
            try:
                move = input("Enter row and column (e.g., 3 4): ")
                r, c = map(int, move.split())
            except:
                print("Invalid input. Please enter two numbers.")
                time.sleep(1)
                continue
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                print("Invalid move. Out of bounds.")
                time.sleep(1)
                continue
            if self.board[r][c] == "B":
                self.revealed[r][c] = True
                self.display_board()
                print(Fore.RED + Style.BRIGHT + "BOOM! You hit a bomb. Game over!" + Style.RESET_ALL)
                self.game_over = True
            else:
                self.reveal(r, c)
                if self.check_win():
                    self.display_board()
                    print(Fore.MAGENTA + Style.BRIGHT + "Congratulations! You cleared the board!" + Style.RESET_ALL)
                    self.game_over = True

    def check_win(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if not self.revealed[i][j] and self.board[i][j] != "B":
                    return False
        return True

def main():
    print(Fore.BLUE + Style.BRIGHT + "Welcome to Minesweeper!")
    time.sleep(1)
    game = Minesweeper(rows=10, cols=10, bombs=12)
    game.play()

if __name__ == "__main__":
    main()
