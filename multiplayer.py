import pygame
import sys
import math
import numpy as np

# Colors
BACKGROUND = (240, 240, 240)
BOARD_BLUE = (52, 152, 219)
EMPTY_CELL = (255, 255, 255)
PLAYER_COLOR = (231, 76, 60)
AI_COLOR = (241, 196, 15)
TEXT_COLOR = (44, 62, 80)
HOVER_COLOR = (189, 195, 199)
WIN_COLOR = (46, 204, 113)  # Color for highlighting winning chips

ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)

# Initialize fonts globally
pygame.font.init()
GAME_FONT = pygame.font.SysFont("monospace", 75)
BUTTON_FONT = pygame.font.SysFont("monospace", 50)

# Create an empty board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

# Drop a piece into the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Check if a column is valid for play
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

# Find the next open row in a column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

# Check for a winning move
def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False

# Draw the board
def draw_board(board, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BOARD_BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, EMPTY_CELL, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, PLAYER_COLOR, (int(c * SQUARESIZE + SQUARESIZE / 2), (ROW_COUNT + 1) * SQUARESIZE - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, AI_COLOR, (int(c * SQUARESIZE + SQUARESIZE / 2), (ROW_COUNT + 1) * SQUARESIZE - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    pygame.display.update()

def display_winner(screen, winner):
    smaller_font = pygame.font.SysFont("monospace", 50)  # Use a smaller font size
    if winner == 1:
        text = smaller_font.render("Player1 Wins", True, TEXT_COLOR)
    elif winner == 2:
        text = smaller_font.render("Player2 Wins", True, TEXT_COLOR)
    else:
        text = smaller_font.render("It's a Tie!", True, TEXT_COLOR)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, SQUARESIZE // 2 - text.get_height() // 2))
    pygame.display.update()

def draw_retry_button(screen):
    smaller_button_font = pygame.font.SysFont("monospace", 40)  # Use a smaller font size
    retry_button = pygame.Rect(screen.get_width() // 2 + 150, SQUARESIZE // 2 - 25, 200, 50)
    pygame.draw.rect(screen, HOVER_COLOR, retry_button)
    text = smaller_button_font.render("Retry", True, TEXT_COLOR)
    screen.blit(text, (retry_button.x + (retry_button.width - text.get_width()) // 2, retry_button.y + (retry_button.height - text.get_height()) // 2))
    return retry_button


# Start the game
def start_game():
    board = create_board()
    game_over = False
    turn = 0
    winner = None

    pygame.init()

    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)

    screen = pygame.display.set_mode(size)
    screen.fill(BACKGROUND)
    draw_board(board, screen)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, PLAYER_COLOR, (posx, SQUARESIZE // 2), RADIUS)
                else:
                    pygame.draw.circle(screen, AI_COLOR, (posx, SQUARESIZE // 2), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1 if turn == 0 else 2)

                    if winning_move(board, 1 if turn == 0 else 2):
                        winner = 1 if turn == 0 else 2
                        game_over = True

                    draw_board(board, screen)
                    turn = (turn + 1) % 2

        if game_over:
            retry_button = draw_retry_button(screen)
            display_winner(screen, winner)
            pygame.display.update()

            retry = False
            while not retry:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if retry_button.collidepoint(pos):
                            retry = True
                            break

            if retry:
                start_game()

if __name__ == "__main__":
    start_game()
