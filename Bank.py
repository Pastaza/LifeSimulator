import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Banking System")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Balance file
BALANCE_FILE = "/home/zach/Banking life sim/balance.txt"

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            try:
                return float(f.read())
            except (ValueError, IOError):
                return 1000.0
    return 1000.0

def save_balance(balance):
    with open(BALANCE_FILE, 'w') as f:
        f.write(str(balance))

# Bank account
balance = load_balance()

# Input box
input_box = pygame.Rect(300, 300, 200, 50)
input_text = ""
input_active = False

# Buttons
deposit_button = pygame.Rect(150, 350, 150, 50)
withdraw_button = pygame.Rect(350, 350, 150, 50)
balance_button = pygame.Rect(550, 350, 150, 50)
exit_button = pygame.Rect(350, 450, 150, 50)
confirm_button = pygame.Rect(325, 400, 150, 50)
back_button = pygame.Rect(20, 550, 100, 30)


# Message
message = ""
message_color = BLACK

# Game state
state = "main_menu"

# Interest timer
interest_rate = 0.0375
last_interest_time = pygame.time.get_ticks()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def bank_main():
    global input_text, input_active, balance, message, message_color, state, last_interest_time

    running = True
    while running:
        screen.fill(WHITE)

        # Interest calculation
        current_time = pygame.time.get_ticks()
        if current_time - last_interest_time > 60000: # 1 minute
            balance *= (1 + interest_rate)
            save_balance(balance)
            last_interest_time = current_time
            message = f"You earned interest! New balance: ${balance:.2f}"
            message_color = GREEN

        # Draw balance
        balance_text = font.render(f"Balance: ${balance:.2f}", 1, BLACK)
        screen.blit(balance_text, (30, 30))

        # Draw timer
        time_remaining = 60 - (current_time - last_interest_time) // 1000
        timer_text = font.render(f"Next interest in: {time_remaining}s", 1, BLACK)
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if state == "main_menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if deposit_button.collidepoint(event.pos):
                        state = "deposit"
                        input_text = ""
                        message = ""
                    elif withdraw_button.collidepoint(event.pos):
                        state = "withdraw"
                        input_text = ""
                        message = ""
                    elif balance_button.collidepoint(event.pos):
                        message = f"Current balance: ${balance:.2f}"
                        message_color = BLACK
                    elif exit_button.collidepoint(event.pos):
                        running = False
                        pygame.quit()
                        sys.exit()

            elif state in ["deposit", "withdraw"]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        input_active = not input_active
                    else:
                        input_active = False

                    if confirm_button.collidepoint(event.pos):
                        try:
                            amount = float(input_text)
                            if state == "deposit":
                                if amount > 0:
                                    balance += amount
                                    save_balance(balance)
                                    message = f"Deposited ${amount:.2f}"
                                    message_color = GREEN
                                else:
                                    message = "Invalid amount"
                                    message_color = RED
                            elif state == "withdraw":
                                if 0 < amount <= balance:
                                    balance -= amount
                                    save_balance(balance)
                                    message = f"Withdrew ${amount:.2f}"
                                    message_color = GREEN
                                elif amount > balance:
                                    message = "Insufficient funds"
                                    message_color = RED
                                else:
                                    message = "Invalid amount"
                                    message_color = RED
                            input_text = ""
                            state = "main_menu"
                        except ValueError:
                            message = "Invalid input"
                            message_color = RED
                    
                    if back_button.collidepoint(event.pos):
                        state = "main_menu"
                        message = ""


                if event.type == pygame.KEYDOWN:
                    if input_active:
                        if event.key == pygame.K_RETURN:
                            # Deactivate input box on enter
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode
        
        # State-based rendering
        if state == "main_menu":
            # Draw title
            draw_text("MarketForge", title_font, BLACK, screen, SCREEN_WIDTH // 2, 150)
            draw_text("Bank", title_font, BLACK, screen, SCREEN_WIDTH // 2, 220)

            draw_rounded_rect(screen, deposit_button, GREEN, 15)
            draw_text("Deposit", font, BLACK, screen, deposit_button.centerx, deposit_button.centery)
            draw_rounded_rect(screen, withdraw_button, RED, 15)
            draw_text("Withdraw", font, BLACK, screen, withdraw_button.centerx, withdraw_button.centery)
            draw_rounded_rect(screen, balance_button, GRAY, 15)
            draw_text("Balance", font, BLACK, screen, balance_button.centerx, balance_button.centery)
            draw_rounded_rect(screen, exit_button, GRAY, 15)
            draw_text("Exit", font, BLACK, screen, exit_button.centerx, exit_button.centery)
        
        elif state == "deposit":
            draw_text("Enter amount to deposit:", font, BLACK, screen, SCREEN_WIDTH // 2, 200)
            # Draw input box
            pygame.draw.rect(screen, BLACK if input_active else GRAY, input_box, 2, border_radius=15)
            draw_text(input_text, font, BLACK, screen, input_box.centerx, input_box.centery)
            # Draw confirm button
            draw_rounded_rect(screen, confirm_button, GREEN, 15)
            draw_text("Deposit", font, BLACK, screen, confirm_button.centerx, confirm_button.centery)
            # Draw back button
            draw_rounded_rect(screen, back_button, GRAY, 15)
            draw_text("Back", font, BLACK, screen, back_button.centerx, back_button.centery)


        elif state == "withdraw":
            draw_text("Enter amount to withdraw:", font, BLACK, screen, SCREEN_WIDTH // 2, 200)
            # Draw input box
            pygame.draw.rect(screen, BLACK if input_active else GRAY, input_box, 2, border_radius=15)
            draw_text(input_text, font, BLACK, screen, input_box.centerx, input_box.centery)
            # Draw confirm button
            draw_rounded_rect(screen, confirm_button, RED, 15)
            draw_text("Withdraw", font, BLACK, screen, confirm_button.centerx, confirm_button.centery)
            # Draw back button
            draw_rounded_rect(screen, back_button, GRAY, 15)
            draw_text("Back", font, BLACK, screen, back_button.centerx, back_button.centery)


        # Draw message
        if message:
            draw_text(message, font, message_color, screen, SCREEN_WIDTH // 2, 500)

        pygame.display.flip()

if __name__ == "__main__":
    bank_main()
