import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Buttons
start_button = pygame.Rect(325, 250, 150, 50)
games_button = pygame.Rect(325, 325, 150, 50)
crypto_button = pygame.Rect(325, 400, 150, 50)
exit_button = pygame.Rect(325, 475, 150, 50)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def main_menu():
    running = True
    while running:
        screen.fill(WHITE)

        draw_text("Life Simulator", title_font, BLACK, screen, SCREEN_WIDTH // 2, 150)

        draw_rounded_rect(screen, start_button, GREEN, 15)
        draw_text("Start Banking", font, BLACK, screen, start_button.centerx, start_button.centery)
        draw_rounded_rect(screen, games_button, GREEN, 15)
        draw_text("Games", font, BLACK, screen, games_button.centerx, games_button.centery)
        draw_rounded_rect(screen, crypto_button, GREEN, 15)
        draw_text("Crypto", font, BLACK, screen, crypto_button.centerx, crypto_button.centery)
        draw_rounded_rect(screen, exit_button, GRAY, 15)
        draw_text("Exit", font, BLACK, screen, exit_button.centerx, exit_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    import Bank
                    Bank.bank_main()
                elif games_button.collidepoint(event.pos):
                    import games_menu
                    games_menu.games_menu()
                elif crypto_button.collidepoint(event.pos):
                    import crypto_trading
                    crypto_trading.crypto_main()
                elif exit_button.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
