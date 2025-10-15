import pygame
import sys
import json
import os

# Initialize Pygame
pygame.init()

# --- Screen and Scaling Setup ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pygame.display.set_caption("Education Center")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200); RED = (255, 0, 0); BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- Data and Utility Functions ---
PORTFOLIO_FILE = "portfolio.json"
COURSES = [
    {"name": "Business Certificate", "cost": 500, "duration": 30},
    {"name": "Programming Bootcamp", "cost": 2000, "duration": 90},
    {"name": "Finance Degree", "cost": 15000, "duration": 365},
    {"name": "Computer Science Degree", "cost": 20000, "duration": 365},
]

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f: return json.load(f)
    return {}

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(data, f, indent=2)

def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# --- Main Loop ---
def education_main(is_fullscreen_initial=False):
    global screen, virtual_screen
    is_fullscreen = is_fullscreen_initial

    buttons = {}
    y_pos = 150
    for course in COURSES:
        rect = pygame.Rect(100, y_pos, 600, 50)
        buttons[course['name']] = {"rect": rect, "course": course}
        y_pos += 70

    back_button = pygame.Rect(20, 550, 100, 30)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)
    message, message_color = "", BLACK
    bill_message, bill_message_timer = "", 0

    running = True
    while running:
        portfolio = load_portfolio()
        game_day = portfolio.get("game_day", 1)

        # --- Monthly Bills and Updates ---
        if game_day > portfolio.get("last_bill_day", 0) and game_day % 30 == 0:
            bills = portfolio.get("bills", {})
            total_bills = sum(bills.values())
            portfolio["bank_balance"] -= total_bills
            portfolio["last_bill_day"] = game_day
            # Property Appreciation
            for prop in portfolio.get("real_estate", {}).get("owned_properties", []):
                prop["market_value"] = prop.get("market_value", prop["price"]) * (1 + prop["appreciation"] / 12)
            save_portfolio(portfolio)
            bill_message, bill_message_timer = f"Monthly bills (${total_bills:,.2f}) paid!", pygame.time.get_ticks() + 4000

        user_education = portfolio.get("education", [])
        cash_on_hand = portfolio.get("cash_on_hand", 0)

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
                elif back_button.collidepoint(mouse_pos):
                    running = False
                for name, data in buttons.items():
                    if data['rect'].collidepoint(mouse_pos):
                        course = data['course']
                        if name not in user_education:
                            if cash_on_hand >= course['cost']:
                                portfolio["cash_on_hand"] -= course['cost']
                                portfolio["education"].append(name)
                                portfolio["game_day"] = portfolio.get("game_day", 1) + course['duration']
                                save_portfolio(portfolio)
                                message, message_color = f"Completed {name}!", GREEN
                            else:
                                message, message_color = "Not enough cash to enroll.", RED
                        else:
                            message, message_color = "You already have this education.", BLUE

        # --- Drawing (on virtual_screen) ---
        virtual_screen.fill(WHITE)
        draw_text(virtual_screen, "Education Center", title_font, BLACK, VIRTUAL_WIDTH // 2, 70)
        draw_text(virtual_screen, f"Cash: ${cash_on_hand:.2f}", font, BLACK, VIRTUAL_WIDTH - 150, 20, center=False)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        for name, data in buttons.items():
            rect = data['rect']
            course = data['course']
            already_have = name in user_education
            can_afford = cash_on_hand >= course['cost']
            color = GRAY if already_have else (WHITE if can_afford else RED)
            pygame.draw.rect(virtual_screen, BLACK, rect, 2, border_radius=10)
            pygame.draw.rect(virtual_screen, color, rect.inflate(-4, -4), border_radius=8)
            draw_text(virtual_screen, course['name'], font, BLACK, rect.left + 15, rect.centery, center=False)
            draw_text(virtual_screen, f"${course['cost']:,}", font, BLACK, rect.centerx, rect.centery)
            draw_text(virtual_screen, f"{course['duration']} days", font, BLACK, rect.right - 150, rect.centery)

        if message: draw_text(virtual_screen, message, small_font, message_color, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 80)
        if bill_message and pygame.time.get_ticks() < bill_message_timer: draw_text(virtual_screen, bill_message, small_font, GREEN, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 40)
        draw_rounded_rect(virtual_screen, back_button, GRAY, 15)
        draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)

        # --- Scale and Update Real Screen ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    education_main()