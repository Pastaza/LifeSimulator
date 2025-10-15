import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# --- Screen and Scaling Setup ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pygame.display.set_caption("Snake")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); RED = (255, 0, 0); GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)

# --- Utility Functions ---
def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# --- Game Loop ---
def game_loop(is_fullscreen_initial=False):
    global screen, virtual_screen
    is_fullscreen = is_fullscreen_initial

    clock = pygame.time.Clock()
    block_size = 20
    snake_speed = 13

    paused = False
    x1, y1 = VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT / 2
    x1_change, y1_change = 0, 0
    snake_list, length_of_snake = [], 1
    foodx = round(random.randrange(0, VIRTUAL_WIDTH - block_size) / block_size) * block_size
    foody = round(random.randrange(0, VIRTUAL_HEIGHT - block_size) / block_size) * block_size

    resume_button = pygame.Rect(325, 250, 150, 50)
    reset_button = pygame.Rect(325, 325, 150, 50)
    back_button = pygame.Rect(325, 400, 150, 50)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)

    def game_over_screen():
        # This screen will also be scaled
        draw_text(virtual_screen, "You Lost! Press C-Play Again or Q-Quit", font, RED, VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT / 2)
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: return True
                    if event.key == pygame.K_c: return False
                if event.type == pygame.QUIT: return True

    while True:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT: x1_change, y1_change = -block_size, 0
                    elif event.key == pygame.K_RIGHT: x1_change, y1_change = block_size, 0
                    elif event.key == pygame.K_UP: y1_change, x1_change = -block_size, 0
                    elif event.key == pygame.K_DOWN: y1_change, x1_change = block_size, 0
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
                if paused:
                    if resume_button.collidepoint(mouse_pos): paused = False
                    elif reset_button.collidepoint(mouse_pos): return is_fullscreen, False # Restart
                    elif back_button.collidepoint(mouse_pos): return is_fullscreen, False # Go back

        # --- Game Logic ---
        if not paused:
            if x1 >= VIRTUAL_WIDTH or x1 < 0 or y1 >= VIRTUAL_HEIGHT or y1 < 0:
                if game_over_screen(): return is_fullscreen, True
                else: return is_fullscreen, False # Restart
            x1 += x1_change
            y1 += y1_change
            snake_head = [x1, y1]
            snake_list.append(snake_head)
            if len(snake_list) > length_of_snake: del snake_list[0]
            if snake_head in snake_list[:-1]:
                if game_over_screen(): return is_fullscreen, True
                else: return is_fullscreen, False # Restart
            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, VIRTUAL_WIDTH - block_size) / block_size) * block_size
                foody = round(random.randrange(0, VIRTUAL_HEIGHT - block_size) / block_size) * block_size
                length_of_snake += 1

        # --- Drawing ---
        virtual_screen.fill(BLACK)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", pygame.font.Font(None, 28), BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        if paused:
            draw_text(virtual_screen, "Paused", font, WHITE, VIRTUAL_WIDTH / 2, 150)
            draw_rounded_rect(virtual_screen, resume_button, GREEN, 15); draw_text(virtual_screen, "Resume", font, BLACK, resume_button.centerx, resume_button.centery)
            draw_rounded_rect(virtual_screen, reset_button, GREEN, 15); draw_text(virtual_screen, "Reset", font, BLACK, reset_button.centerx, reset_button.centery)
            draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)
        else:
            pygame.draw.rect(virtual_screen, RED, [foodx, foody, block_size, block_size])
            for segment in snake_list:
                pygame.draw.rect(virtual_screen, GREEN, [segment[0], segment[1], block_size, block_size])

        # --- Scale and Update ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(snake_speed)

def snake_main(is_fullscreen_initial=False):
    is_fullscreen, should_quit = game_loop(is_fullscreen_initial)
    if should_quit:
        pygame.quit()
        sys.exit()
    return is_fullscreen, False

if __name__ == '__main__':
    snake_main()