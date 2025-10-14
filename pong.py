
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Game variables
clock = pygame.time.Clock()

# Paddles and ball
paddle_width = 15
paddle_height = 100
ball_size = 15

player_paddle = pygame.Rect(50, SCREEN_HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)
ai_paddle = pygame.Rect(SCREEN_WIDTH - 50 - paddle_width, SCREEN_HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)
ball = pygame.Rect(SCREEN_WIDTH / 2 - ball_size / 2, SCREEN_HEIGHT / 2 - ball_size / 2, ball_size, ball_size)

ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
player_speed = 0
ai_speed = 8

font = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 36)

resume_button = pygame.Rect(325, 250, 150, 50)
reset_button = pygame.Rect(325, 325, 150, 50)
back_button = pygame.Rect(325, 400, 150, 50)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def game_loop():
    global ball_speed_x, ball_speed_y, player_speed

    player_score = 0
    ai_score = 0
    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_UP:
                        player_speed = -10
                    if event.key == pygame.K_DOWN:
                        player_speed = 10
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player_speed = 0
            if event.type == pygame.MOUSEBUTTONDOWN and paused:
                if resume_button.collidepoint(event.pos):
                    paused = False
                elif reset_button.collidepoint(event.pos):
                    return game_loop()
                elif back_button.collidepoint(event.pos):
                    return False

        if paused:
            draw_text("Paused", font, WHITE, screen, SCREEN_WIDTH / 2, 150)
            draw_rounded_rect(screen, resume_button, GREEN, 15)
            draw_text("Resume", font_small, BLACK, screen, resume_button.centerx, resume_button.centery)
            draw_rounded_rect(screen, reset_button, GREEN, 15)
            draw_text("Reset", font_small, BLACK, screen, reset_button.centerx, reset_button.centery)
            draw_rounded_rect(screen, back_button, GRAY, 15)
            draw_text("Back", font_small, BLACK, screen, back_button.centerx, back_button.centery)

            pygame.display.update()
            clock.tick(15)
            continue

        # Move player paddle
        player_paddle.y += player_speed
        if player_paddle.top <= 0:
            player_paddle.top = 0
        if player_paddle.bottom >= SCREEN_HEIGHT:
            player_paddle.bottom = SCREEN_HEIGHT

        # Move AI paddle
        if ai_paddle.top < ball.y:
            ai_paddle.y += ai_speed
        if ai_paddle.bottom > ball.y:
            ai_paddle.y -= ai_speed
        if ai_paddle.top <= 0:
            ai_paddle.top = 0
        if ai_paddle.bottom >= SCREEN_HEIGHT:
            ai_paddle.bottom = SCREEN_HEIGHT

        # Move ball
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1
        if ball.left <= 0:
            ai_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x *= random.choice((1, -1))
            ball_speed_y *= random.choice((1, -1))
        if ball.right >= SCREEN_WIDTH:
            player_score += 1
            ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            ball_speed_x *= random.choice((1, -1))
            ball_speed_y *= random.choice((1, -1))

        if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
            ball_speed_x *= -1

        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, ai_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH / 2, 0), (SCREEN_WIDTH / 2, SCREEN_HEIGHT))

        player_text = font.render(str(player_score), True, WHITE)
        screen.blit(player_text, (SCREEN_WIDTH / 4, 20))

        ai_text = font.render(str(ai_score), True, WHITE)
        screen.blit(ai_text, (SCREEN_WIDTH * 3 / 4, 20))

        pygame.display.flip()
        clock.tick(60)

def pong_main():
    if game_loop():
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pong_main()
