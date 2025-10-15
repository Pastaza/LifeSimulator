import pygame
import sys
import os
import json

# Initialize Pygame
pygame.init()

# --- Screen and Scaling Setup ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600

screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

pygame.display.set_caption("Banking System")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (200, 200, 200); RED = (255, 0, 0); GREEN = (0, 255, 0)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# Portfolio file
PORTFOLIO_FILE = "portfolio.json"

# --- Data and Utility Functions ---
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            try: return json.load(f)
            except (json.JSONDecodeError, IOError): pass
    return {"bank_balance": 1000.0, "cash_on_hand": 100.0}

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# --- Bank Main Loop ---
def bank_main(is_fullscreen_initial=False):
    global screen, virtual_screen
    portfolio = load_portfolio()
    bank_balance = portfolio.get("bank_balance", 1000.0)
    cash_on_hand = portfolio.get("cash_on_hand", 100.0)

    input_text, message, state = "", "", "main_menu"
    message_color, input_active = BLACK, False
    is_fullscreen = is_fullscreen_initial

    last_interest_time = pygame.time.get_ticks()

    # Buttons
    deposit_button = pygame.Rect(200, 350, 150, 50)
    withdraw_button = pygame.Rect(450, 350, 150, 50)
    exit_button = pygame.Rect(325, 450, 150, 50)
    confirm_button = pygame.Rect(325, 400, 150, 50)
    back_button = pygame.Rect(20, 550, 100, 30)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)
    input_box = pygame.Rect(300, 300, 200, 50)

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
                elif state == "main_menu":
                    if deposit_button.collidepoint(mouse_pos): state, input_text, message = "deposit", "", ""
                    elif withdraw_button.collidepoint(mouse_pos): state, input_text, message = "withdraw", "", ""
                    elif exit_button.collidepoint(mouse_pos): running = False
                elif state in ["deposit", "withdraw"]:
                    input_active = input_box.collidepoint(mouse_pos)
                    if back_button.collidepoint(mouse_pos): state, message = "main_menu", ""
                    if confirm_button.collidepoint(mouse_pos):
                        try:
                            amount = float(input_text)
                            if state == "deposit" and 0 < amount <= cash_on_hand:
                                cash_on_hand -= amount; bank_balance += amount
                                message, message_color = f"Deposited ${amount:.2f}", GREEN
                            elif state == "withdraw" and 0 < amount <= bank_balance:
                                bank_balance -= amount; cash_on_hand += amount
                                message, message_color = f"Withdrew ${amount:.2f}", GREEN
                            else:
                                message, message_color = "Invalid amount or insufficient funds.", RED
                            portfolio["bank_balance"] = bank_balance; portfolio["cash_on_hand"] = cash_on_hand
                            save_portfolio(portfolio)
                            input_text, state = "", "main_menu"
                        except ValueError: message, message_color = "Invalid input", RED
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() or (event.unicode == '.' and '.' not in input_text):
                    input_text += event.unicode

        # --- Drawing (on virtual_screen) ---
        virtual_screen.fill(WHITE)
        draw_text(virtual_screen, f"Bank: ${bank_balance:.2f}", font, BLACK, 200, 30, False)
        draw_text(virtual_screen, f"Cash: ${cash_on_hand:.2f}", font, BLACK, 200, 70, False)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        if state == "main_menu":
            draw_text(virtual_screen, "Bank", title_font, BLACK, VIRTUAL_WIDTH // 2, 220)
            draw_rounded_rect(virtual_screen, deposit_button, GREEN, 15); draw_text(virtual_screen, "Deposit", font, BLACK, deposit_button.centerx, deposit_button.centery)
            draw_rounded_rect(virtual_screen, withdraw_button, RED, 15); draw_text(virtual_screen, "Withdraw", font, BLACK, withdraw_button.centerx, withdraw_button.centery)
            draw_rounded_rect(virtual_screen, exit_button, GRAY, 15); draw_text(virtual_screen, "Back to Menu", font, BLACK, exit_button.centerx, exit_button.centery)
        else:
            draw_text(virtual_screen, f"Enter amount to {state}:", font, BLACK, VIRTUAL_WIDTH // 2, 200)
            pygame.draw.rect(virtual_screen, BLACK if input_active else GRAY, input_box, 2, border_radius=15)
            draw_text(virtual_screen, input_text, font, BLACK, input_box.centerx, input_box.centery)
            btn_color = GREEN if state == "deposit" else RED
            draw_rounded_rect(virtual_screen, confirm_button, btn_color, 15); draw_text(virtual_screen, state.capitalize(), font, BLACK, confirm_button.centerx, confirm_button.centery)
            draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)

        if message: draw_text(virtual_screen, message, font, message_color, VIRTUAL_WIDTH // 2, 500)

        # --- Scale and Update Real Screen ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    bank_main()