import pygame
import sys
import math
import numpy as np
import random
import time

# Colors
BACKGROUND = (240, 240, 240)
BOARD_BLUE = (52, 152, 219)
EMPTY_CELL = (255, 255, 255)
PLAYER_COLOR = (231, 76, 60)
AI_COLOR = (241, 196, 15)
TEXT_COLOR = (44, 62, 80)
HOVER_COLOR = (189, 195, 199)
WIN_COLOR = (46, 204, 113)  # Color for highlighting winning chips

# Board dimensions
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)

# Initialize Pygame
pygame.init()

# Fonts
TITLE_FONT = pygame.font.SysFont("Arial", 80, bold=True)
BUTTON_FONT = pygame.font.SysFont("Arial", 40, bold=True)
GAME_FONT = pygame.font.SysFont("Arial", 60, bold=True)

# Static Move Order (center first)
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]

# Zobrist hashing for transposition table
zobrist_table = np.random.randint(0, 2**64, (ROW_COUNT, COLUMN_COUNT, 2), dtype=np.uint64)

def zobrist_hash(board):
    """Generate a Zobrist hash for the board."""
    hash_value = np.uint64(0)  # Ensure hash_value is of type np.uint64
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            if board[r][c] != 0:
                hash_value ^= zobrist_table[r][c][int(board[r][c]) - 1]
    return hash_value

# Transposition table
transposition_table = {}

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)  # Use int instead of float

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
    return None

def winning_move(board, piece):
    # Horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]  # Return winning positions

    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]  # Return winning positions

    # Diagonal (positive slope)
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]  # Return winning positions

    # Diagonal (negative slope)
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return [(r - i, c + i) for i in range(4)]  # Return winning positions

    return None

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def evaluate_position(board, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2

    # Center column control
    center_array = [int(board[r][COLUMN_COUNT // 2]) for r in range(ROW_COUNT)]
    center_count = center_array.count(piece)
    score += center_count * 6  # Increased weight for center control

    # Evaluate all possible windows
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            # Horizontal
            if c <= COLUMN_COUNT - 4:
                window = [board[r][c + i] for i in range(4)]
                score += evaluate_window(window, piece)

            # Vertical
            if r <= ROW_COUNT - 4:
                window = [board[r + i][c] for i in range(4)]
                score += evaluate_window(window, piece)

            # Positive slope diagonal
            if r <= ROW_COUNT - 4 and c <= COLUMN_COUNT - 4:
                window = [board[r + i][c + i] for i in range(4)]
                score += evaluate_window(window, piece)

            # Negative slope diagonal
            if r >= 3 and c <= COLUMN_COUNT - 4:
                window = [board[r - i][c + i] for i in range(4)]
                score += evaluate_window(window, piece)

    # Penalize opponent's potential wins
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            if board[r][c] == opp_piece:
                # Check for potential wins
                if c <= COLUMN_COUNT - 4 and all(board[r][c + i] == opp_piece for i in range(4)):
                    score -= 100  # Heavy penalty for opponent's win
                if r <= ROW_COUNT - 4 and all(board[r + i][c] == opp_piece for i in range(4)):
                    score -= 100
                if r <= ROW_COUNT - 4 and c <= COLUMN_COUNT - 4 and all(board[r + i][c + i] == opp_piece for i in range(4)):
                    score -= 100
                if r >= 3 and c <= COLUMN_COUNT - 4 and all(board[r - i][c + i] == opp_piece for i in range(4)):
                    score -= 100

    return score

def order_moves(board, valid_locations, piece):
    scores = []
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = evaluate_position(temp_board, piece)
        scores.append((col, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scores]

def iterative_deepening(board, max_depth, time_limit):
    """Iterative deepening with time limit."""
    start_time = time.time()
    best_move = None
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        best_move, _ = minimax(board, depth, -math.inf, math.inf, True)
    return best_move

def minimax(board, depth, alpha, beta, maximizingPlayer):
    board_key = zobrist_hash(board)
    if board_key in transposition_table:
        entry = transposition_table[board_key]
        if entry["depth"] >= depth:
            if entry["flag"] == "exact":
                return entry["move"], entry["value"]
            elif entry["flag"] == "lower":
                alpha = max(alpha, entry["value"])
            elif entry["flag"] == "upper":
                beta = min(beta, entry["value"])
            if alpha >= beta:
                return entry["move"], entry["value"]

    valid_locations = [col for col in MOVE_ORDER if is_valid_location(board, col)]
    is_terminal = winning_move(board, 1) or winning_move(board, 2) or len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 1e9)
            elif winning_move(board, 1):
                return (None, -1e9)
            else:
                return (None, 0)
        else:
            return (None, evaluate_position(board, 2))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if value <= alpha:
            flag = "upper"
        elif value >= beta:
            flag = "lower"
        else:
            flag = "exact"
        transposition_table[board_key] = {"move": column, "value": value, "depth": depth, "flag": flag}
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        if value <= alpha:
            flag = "upper"
        elif value >= beta:
            flag = "lower"
        else:
            flag = "exact"
        transposition_table[board_key] = {"move": column, "value": value, "depth": depth, "flag": flag}
        return column, value

def draw_board(screen, board, winning_positions=None):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BOARD_BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, EMPTY_CELL, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                color = PLAYER_COLOR
                if winning_positions and (r, c) in winning_positions:
                    color = WIN_COLOR  # Highlight winning chips
                pygame.draw.circle(screen, color, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                color = AI_COLOR
                if winning_positions and (r, c) in winning_positions:
                    color = WIN_COLOR  # Highlight winning chips
                pygame.draw.circle(screen, color, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

def display_winner(screen, winner):
    """Display the winner on the screen."""
    if winner == 1:
        text = GAME_FONT.render("Player 1 Wins!", True, TEXT_COLOR)
    elif winner == 2:
        text = GAME_FONT.render("AI Wins!", True, TEXT_COLOR)
    else:
        text = GAME_FONT.render("It's a Tie!", True, TEXT_COLOR)
    screen.blit(text, (width // 2 - text.get_width() // 2, SQUARESIZE // 2 - text.get_height() // 2))
    pygame.display.update()

def draw_retry_button(screen):
    """Draw the retry button on the screen."""
    retry_button = pygame.Rect(width // 2 + 150, SQUARESIZE // 2 - 25, 200, 50)
    pygame.draw.rect(screen, BACKGROUND, retry_button)
    text = BUTTON_FONT.render("Retry", True, TEXT_COLOR)
    screen.blit(text, (width // 2 + 150 + (200 - text.get_width()) // 2, SQUARESIZE // 2 - 25 + (50 - text.get_height()) // 2))
    return retry_button

def player_selection_screen():
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Connect 4 - Player Selection")
    
    while True:
        screen.fill(BACKGROUND)
        
        title = TITLE_FONT.render("Who starts?", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        if draw_button(screen, "Player", SCREEN_WIDTH//2 - 250, 250, 200, 80, PLAYER_COLOR, HOVER_COLOR):
            return True
        if draw_button(screen, "AI", SCREEN_WIDTH//2 + 50, 250, 200, 80, AI_COLOR, HOVER_COLOR):
            return False
            
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def draw_button(screen, text, x, y, w, h, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    button_rect = pygame.Rect(x, y, w, h)
    if button_rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, button_rect)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, color, button_rect)
        
    text_surface = BUTTON_FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return False

def start_game():
    player_starts = player_selection_screen()
    board = create_board()
    game_over = False
    winner = None
    winning_positions = None
    pygame.init()

    global width, height
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect 4")
    draw_board(screen, board)

    turn = 0 if player_starts else 1

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, PLAYER_COLOR, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, width, SQUARESIZE))
                if turn == 0:
                    posx = event.pos[0]
                    col = posx // SQUARESIZE

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)

                        winning_positions = winning_move(board, 1)
                        if winning_positions:
                            winner = 1
                            game_over = True

                        turn = 1
                        draw_board(screen, board, winning_positions)

        if turn == 1 and not game_over:
            col = iterative_deepening(board, 6, 2) 
            if is_valid_location(board, col):
                pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                winning_positions = winning_move(board, 2)
                if winning_positions:
                    winner = 2
                    game_over = True

                turn = 0
                draw_board(screen, board, winning_positions)

        if game_over:
            retry_button = draw_retry_button(screen)
            display_winner(screen, winner)
            pygame.display.update()

            # Wait for retry button click
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
                start_game()  # Restart the game

if __name__ == "__main__":
    start_game()