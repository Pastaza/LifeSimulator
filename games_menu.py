import pygame
import sys

# Initialize Pygame
pygame.init()

# --- Screen and Scaling Setup ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pygame.display.set_caption("Games Menu")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- Utility Functions ---
def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# --- Main Loop ---
def games_menu(is_fullscreen_initial=False):
    global screen, virtual_screen
    is_fullscreen = is_fullscreen_initial

    snake_button = pygame.Rect(325, 250, 150, 50)
    pong_button = pygame.Rect(325, 325, 150, 50)
    back_button = pygame.Rect(325, 400, 150, 50)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.MOUSEBUTTONDOWN:
                real_screen_size = screen.get_size()
                scale_x = VIRTUAL_WIDTH / real_screen_size[0]
                scale_y = VIRTUAL_HEIGHT / real_screen_size[1]
                mouse_pos = (event.pos[0] * scale_x, event.pos[1] * scale_y)

                if fullscreen_button.collidepoint(mouse_pos):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                elif snake_button.collidepoint(mouse_pos):
                    import snake
                    snake.snake_main(is_fullscreen)
                elif pong_button.collidepoint(mouse_pos):
                    import pong
                    pong.pong_main(is_fullscreen)
                elif back_button.collidepoint(mouse_pos):
                    running = False

        # --- Drawing (on virtual_screen) ---
        virtual_screen.fill(WHITE)
        draw_text(virtual_screen, "Games", title_font, BLACK, VIRTUAL_WIDTH // 2, 150)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        draw_rounded_rect(virtual_screen, snake_button, GREEN, 15); draw_text(virtual_screen, "Snake", font, BLACK, snake_button.centerx, snake_button.centery)
        draw_rounded_rect(virtual_screen, pong_button, GREEN, 15); draw_text(virtual_screen, "Pong", font, BLACK, pong_button.centerx, pong_button.centery)
        draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)

        # --- Scale and Update Real Screen ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    games_menu()