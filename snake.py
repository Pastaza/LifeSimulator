
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Game variables
clock = pygame.time.Clock()
block_size = 20
snake_speed = 15

font = pygame.font.Font(None, 36)

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
    paused = False

    x1 = SCREEN_WIDTH / 2
    y1 = SCREEN_HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    foodx = round(random.randrange(0, SCREEN_WIDTH - block_size) / block_size) * block_size
    foody = round(random.randrange(0, SCREEN_HEIGHT - block_size) / block_size) * block_size

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        x1_change = -block_size
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x1_change = block_size
                        y1_change = 0
                    elif event.key == pygame.K_UP:
                        y1_change = -block_size
                        x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        y1_change = block_size
                        x1_change = 0
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
            draw_text("Resume", font, BLACK, screen, resume_button.centerx, resume_button.centery)
            draw_rounded_rect(screen, reset_button, GREEN, 15)
            draw_text("Reset", font, BLACK, screen, reset_button.centerx, reset_button.centery)
            draw_rounded_rect(screen, back_button, GRAY, 15)
            draw_text("Back", font, BLACK, screen, back_button.centerx, back_button.centery)

            pygame.display.update()
            clock.tick(15)
            continue

        if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
            return game_over_screen()

        x1 += x1_change
        y1 += y1_change
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [foodx, foody, block_size, block_size])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                return game_over_screen()

        for segment in snake_list:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], block_size, block_size])

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, SCREEN_WIDTH - block_size) / block_size) * block_size
            foody = round(random.randrange(0, SCREEN_HEIGHT - block_size) / block_size) * block_size
            length_of_snake += 1

        clock.tick(snake_speed)

def game_over_screen():
    screen.fill(BLACK)
    draw_text("You Lost! Press C-Play Again or Q-Quit", font, RED, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
                if event.key == pygame.K_c:
                    return game_loop()
            if event.type == pygame.QUIT:
                return True

def snake_main():
    if game_loop():
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    snake_main()
