
import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Games Menu")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Buttons
snake_button = pygame.Rect(325, 250, 150, 50)
pong_button = pygame.Rect(325, 325, 150, 50)
back_button = pygame.Rect(325, 400, 150, 50)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def games_menu():
    running = True
    while running:
        screen.fill(WHITE)

        draw_text("Games", title_font, BLACK, screen, SCREEN_WIDTH // 2, 150)

        draw_rounded_rect(screen, snake_button, GREEN, 15)
        draw_text("Snake", font, BLACK, screen, snake_button.centerx, snake_button.centery)
        draw_rounded_rect(screen, pong_button, GREEN, 15)
        draw_text("Pong", font, BLACK, screen, pong_button.centerx, pong_button.centery)
        draw_rounded_rect(screen, back_button, GRAY, 15)
        draw_text("Back", font, BLACK, screen, back_button.centerx, back_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if snake_button.collidepoint(event.pos):
                    import snake
                    snake.snake_main()
                elif pong_button.collidepoint(event.pos):
                    import pong
                    pong.pong_main()
                elif back_button.collidepoint(event.pos):
                    running = False

        pygame.display.flip()

if __name__ == "__main__":
    games_menu()
