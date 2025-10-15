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
pygame.display.set_caption("Main Menu")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200); BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- Data and Utility Functions ---
PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f: return json.load(f)
    # Create a default portfolio if one doesn't exist
    default_portfolio = {
        "bank_balance": 1000.0, "cash_on_hand": 500.0, "game_day": 1, "last_bill_day": 1,
        "current_job": None, "education": [], "assets": {},
        "realized_pnl": {},
        "real_estate": {"owned_properties": [], "current_residence": "Living with Parents"},
        "bills": {"rent_mortgage": 0, "utilities": 50, "living_expenses": 100}
    }
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(default_portfolio, f, indent=2)
    return default_portfolio

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(data, f, indent=2)

def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# --- Main Menu Loop ---
def main_menu():
    global screen, virtual_screen
    is_fullscreen = False
    message, message_timer = "", 0
    last_day_checked = 0

    # Buttons
    work_button = pygame.Rect(50, 150, 200, 60)
    bank_button = pygame.Rect(300, 250, 200, 50)
    trading_button = pygame.Rect(300, 310, 200, 50)
    games_button = pygame.Rect(300, 370, 200, 50)
    jobs_button = pygame.Rect(550, 250, 200, 50)
    education_button = pygame.Rect(550, 310, 200, 50)
    housing_button = pygame.Rect(550, 370, 200, 50)
    exit_button = pygame.Rect(300, 450, 200, 50)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)

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
            message, message_timer = f"Monthly bills (${total_bills:,.2f}) paid!", pygame.time.get_ticks() + 4000

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = (event.pos[0] * (VIRTUAL_WIDTH / screen.get_width()), event.pos[1] * (VIRTUAL_HEIGHT / screen.get_height()))
                if fullscreen_button.collidepoint(mouse_pos):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                elif exit_button.collidepoint(mouse_pos): running = False
                elif work_button.collidepoint(mouse_pos):
                    current_job = portfolio.get("current_job")
                    if current_job:
                        daily_salary = current_job['salary'] / 365
                        portfolio["cash_on_hand"] += daily_salary
                        portfolio["game_day"] += 1
                        save_portfolio(portfolio)
                        message, message_timer = f"You earned ${daily_salary:.2f}!", pygame.time.get_ticks() + 2000
                # ... (Navigation button logic) ...
                elif bank_button.collidepoint(mouse_pos): import Bank; is_fullscreen, _ = Bank.bank_main(is_fullscreen)
                elif trading_button.collidepoint(mouse_pos): import trading_view; is_fullscreen, _ = trading_view.trading_main(is_fullscreen)
                elif games_button.collidepoint(mouse_pos): import games_menu; is_fullscreen, _ = games_menu.games_menu(is_fullscreen)
                elif jobs_button.collidepoint(mouse_pos): import jobs; is_fullscreen, _ = jobs.jobs_main(is_fullscreen)
                elif education_button.collidepoint(mouse_pos): import education; is_fullscreen, _ = education.education_main(is_fullscreen)
                elif housing_button.collidepoint(mouse_pos): import housing; is_fullscreen, _ = housing.housing_main(is_fullscreen)

        # --- Drawing ---
        virtual_screen.fill(WHITE)
        portfolio = load_portfolio()
        game_day = portfolio.get("game_day", 1)
        cash_on_hand = portfolio.get("cash_on_hand", 0)
        current_job = portfolio.get("current_job")

        draw_text(virtual_screen, f"Day: {game_day}", small_font, BLACK, 200, 30)
        draw_text(virtual_screen, f"Cash: ${portfolio['cash_on_hand']:.2f}", small_font, BLACK, VIRTUAL_WIDTH - 200, 30)
        draw_text(virtual_screen, "Life Simulator", title_font, BLACK, VIRTUAL_WIDTH // 2, 70)

        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)

        work_color = GRAY if not current_job else GREEN
        draw_rounded_rect(virtual_screen, work_button, work_color, 15)
        draw_text(virtual_screen, "Go to Work", font, BLACK, work_button.centerx, work_button.centery)
        if current_job:
            daily_salary = current_job['salary'] / 365
            draw_text(virtual_screen, f"(+${daily_salary:.2f})", small_font, BLACK, work_button.centerx, work_button.centery + 25)

        draw_rounded_rect(virtual_screen, bank_button, BLUE, 15); draw_text(virtual_screen, "Bank", font, WHITE, bank_button.centerx, bank_button.centery)
        draw_rounded_rect(virtual_screen, trading_button, BLUE, 15); draw_text(virtual_screen, "Trading", font, WHITE, trading_button.centerx, trading_button.centery)
        draw_rounded_rect(virtual_screen, games_button, BLUE, 15); draw_text(virtual_screen, "Games", font, WHITE, games_button.centerx, games_button.centery)
        draw_rounded_rect(virtual_screen, jobs_button, BLUE, 15); draw_text(virtual_screen, "Job Market", font, WHITE, jobs_button.centerx, jobs_button.centery)
        draw_rounded_rect(virtual_screen, education_button, BLUE, 15); draw_text(virtual_screen, "Education", font, WHITE, education_button.centerx, education_button.centery)
        draw_rounded_rect(virtual_screen, housing_button, BLUE, 15); draw_text(virtual_screen, "Real Estate", font, WHITE, housing_button.centerx, housing_button.centery)
        draw_rounded_rect(virtual_screen, exit_button, GRAY, 15); draw_text(virtual_screen, "Exit", font, BLACK, exit_button.centerx, exit_button.centery)

        if message and pygame.time.get_ticks() < message_timer:
            draw_text(virtual_screen, message, font, GREEN, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 40)

        # --- Scale and Update ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
