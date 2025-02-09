import pygame
import sys
import multiplayer
import ai_game

# Define Colors
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 223, 0)
DARK_BLUE = (0, 0, 139)

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize Pygame
pygame.init()

# Window size
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Connect 4")

# Fonts
title_font = pygame.font.SysFont("monospace", 100, bold=True)
button_font = pygame.font.SysFont("monospace", 50, bold=True)

# Function to display centered text
def draw_text(text, font, color, surface, x, y):
    label = font.render(text, True, color)
    surface.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))

# Function to draw a button
def draw_button(text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, hover_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(text, button_font, BLACK, screen, x + w // 2, y + h // 2)

# Function to display the main menu with buttons
def main_menu():
    menu_open = True
    while menu_open:
        screen.fill(DARK_BLUE)
        draw_text("Connect 4", title_font, YELLOW, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

        draw_button("Multiplayer Mode", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 75, 500, 75, YELLOW, WHITE, multiplayer.start_game)
        draw_button("AI Mode", SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50, 500, 75, YELLOW, WHITE, ai_game.start_game)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Main game function
def game_loop():
    main_menu()

# Start the game loop
game_loop()
