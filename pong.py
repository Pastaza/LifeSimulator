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
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 36)

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
    paddle_width, paddle_height, ball_size = 15, 100, 15
    player_paddle = pygame.Rect(50, VIRTUAL_HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)
    ai_paddle = pygame.Rect(VIRTUAL_WIDTH - 50 - paddle_width, VIRTUAL_HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)
    ball = pygame.Rect(VIRTUAL_WIDTH / 2 - ball_size / 2, VIRTUAL_HEIGHT / 2 - ball_size / 2, ball_size, ball_size)

    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))
    player_speed, ai_speed = 0, 8
    player_score, ai_score = 0, 0
    paused = False

    resume_button = pygame.Rect(325, 250, 150, 50)
    reset_button = pygame.Rect(325, 325, 150, 50)
    back_button = pygame.Rect(325, 400, 150, 50)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)

    while True:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: paused = not paused
                if not paused:
                    if event.key == pygame.K_UP: player_speed = -10
                    if event.key == pygame.K_DOWN: player_speed = 10
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]: player_speed = 0
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
            player_paddle.y += player_speed
            if player_paddle.top <= 0: player_paddle.top = 0
            if player_paddle.bottom >= VIRTUAL_HEIGHT: player_paddle.bottom = VIRTUAL_HEIGHT

            if ai_paddle.top < ball.y: ai_paddle.y += ai_speed
            if ai_paddle.bottom > ball.y: ai_paddle.y -= ai_speed

            ball.x += ball_speed_x
            ball.y += ball_speed_y

            if ball.top <= 0 or ball.bottom >= VIRTUAL_HEIGHT: ball_speed_y *= -1
            if ball.left <= 0: 
                ai_score += 1
                ball.center = (VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT / 2)
                ball_speed_x *= random.choice((1, -1))
            if ball.right >= VIRTUAL_WIDTH:
                player_score += 1
                ball.center = (VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT / 2)
                ball_speed_x *= random.choice((1, -1))
            if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle): ball_speed_x *= -1

        # --- Drawing ---
        virtual_screen.fill(BLACK)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", pygame.font.Font(None, 28), BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        if paused:
            draw_text(virtual_screen, "Paused", font, WHITE, VIRTUAL_WIDTH / 2, 150)
            draw_rounded_rect(virtual_screen, resume_button, GREEN, 15); draw_text(virtual_screen, "Resume", font_small, BLACK, resume_button.centerx, resume_button.centery)
            draw_rounded_rect(virtual_screen, reset_button, GREEN, 15); draw_text(virtual_screen, "Reset", font_small, BLACK, reset_button.centerx, reset_button.centery)
            draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", font_small, BLACK, back_button.centerx, back_button.centery)
        else:
            pygame.draw.rect(virtual_screen, WHITE, player_paddle)
            pygame.draw.rect(virtual_screen, WHITE, ai_paddle)
            pygame.draw.ellipse(virtual_screen, WHITE, ball)
            pygame.draw.aaline(virtual_screen, WHITE, (VIRTUAL_WIDTH / 2, 0), (VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT))
            draw_text(virtual_screen, str(player_score), font, WHITE, VIRTUAL_WIDTH / 4, 20)
            draw_text(virtual_screen, str(ai_score), font, WHITE, VIRTUAL_WIDTH * 3 / 4, 20)

        # --- Scale and Update ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def pong_main(is_fullscreen_initial=False):
    is_fullscreen, should_quit = game_loop(is_fullscreen_initial)
    if should_quit:
        pygame.quit()
        sys.exit()
    return is_fullscreen, False

if __name__ == '__main__':
    pong_main()