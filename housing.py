
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
pygame.display.set_caption("Real Estate Market")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200); RED = (255, 0, 0); BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- Data and Utility Functions ---
PORTFOLIO_FILE = "portfolio.json"
PROPERTIES = [
    {"name": "Studio Apartment", "type": "Apartment", "status": "For Rent", "rent": 800, "utilities": 150, "living": 200},
    {"name": "2-Bed Apartment", "type": "Apartment", "status": "For Rent", "rent": 1400, "utilities": 250, "living": 350},
    {"name": "Suburban Starter Home", "type": "House", "status": "For Sale", "price": 250000, "down_payment_percent": 0.2, "mortgage_years": 30, "interest_rate": 0.05, "utilities": 400, "living": 500, "appreciation": 0.03},
    {"name": "Downtown Condo", "type": "Condo", "status": "For Sale", "price": 400000, "down_payment_percent": 0.2, "mortgage_years": 30, "interest_rate": 0.05, "utilities": 600, "living": 800, "appreciation": 0.04},
    {"name": "Luxury Villa", "type": "House", "status": "For Sale", "price": 1200000, "down_payment_percent": 0.25, "mortgage_years": 30, "interest_rate": 0.045, "utilities": 1500, "living": 2000, "appreciation": 0.05},
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
def housing_main(is_fullscreen_initial=False):
    global screen, virtual_screen
    is_fullscreen = is_fullscreen_initial
    scroll_y = 0
    active_tab = "For Rent"
    message, message_color, message_timer = "", BLACK, 0

    # UI Elements
    back_button = pygame.Rect(20, 550, 100, 30)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)
    rent_tab_button = pygame.Rect(150, 120, 150, 40)
    buy_tab_button = pygame.Rect(310, 120, 150, 40)
    portfolio_tab_button = pygame.Rect(470, 120, 150, 40)

    running = True
    while running:
        portfolio = load_portfolio()
        bank_balance = portfolio.get("bank_balance", 0)
        owned_property_names = [p['name'] for p in portfolio.get("real_estate", {}).get("owned_properties", [])]

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.MOUSEWHEEL: scroll_y = max(0, scroll_y - event.y * 20)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = (event.pos[0] * (VIRTUAL_WIDTH / screen.get_width()), event.pos[1] * (VIRTUAL_HEIGHT / screen.get_height()))
                if fullscreen_button.collidepoint(mouse_pos):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                elif back_button.collidepoint(mouse_pos): running = False
                elif rent_tab_button.collidepoint(mouse_pos): active_tab = "For Rent"; scroll_y = 0
                elif buy_tab_button.collidepoint(mouse_pos): active_tab = "For Sale"; scroll_y = 0
                elif portfolio_tab_button.collidepoint(mouse_pos): active_tab = "Portfolio"; scroll_y = 0
                else:
                    # --- Property Interaction Logic ---
                    y_pos_check = 170 - scroll_y
                    properties_to_check = []
                    if active_tab == "Portfolio": properties_to_check = portfolio.get("real_estate", {}).get("owned_properties", [])
                    else: properties_to_check = [p for p in PROPERTIES if p["status"] == active_tab]

                    for prop in properties_to_check:
                        action_button_rect = pygame.Rect(600, y_pos_check + 30, 120, 40)
                        if action_button_rect.collidepoint(mouse_pos):
                            if active_tab == "For Rent":
                                portfolio["real_estate"]["current_residence"] = prop["name"]
                                portfolio["bills"] = {"rent_mortgage": prop["rent"], "utilities": prop["utilities"], "living_expenses": prop["living"]}
                                message, message_color = f"You are now renting {prop['name']}.", GREEN
                            elif active_tab == "For Sale":
                                down_payment = prop["price"] * prop["down_payment_percent"]
                                if bank_balance >= down_payment:
                                    portfolio["bank_balance"] -= down_payment
                                    new_property = prop.copy()
                                    new_property["purchase_price"] = prop["price"]
                                    new_property["market_value"] = prop["price"]
                                    portfolio["real_estate"]["owned_properties"].append(new_property)
                                    # Simple mortgage calculation
                                    loan = prop["price"] - down_payment
                                    monthly_rate = prop["interest_rate"] / 12
                                    num_payments = prop["mortgage_years"] * 12
                                    mortgage_payment = loan * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                                    portfolio["bills"]["rent_mortgage"] = mortgage_payment
                                    portfolio["bills"]["utilities"] = prop["utilities"]
                                    portfolio["bills"]["living_expenses"] = prop["living"]
                                    portfolio["real_estate"]["current_residence"] = prop["name"]
                                    message, message_color = f"You bought {prop['name']}!", GREEN
                                else:
                                    message, message_color = "Not enough for down payment.", RED
                            elif active_tab == "Portfolio":
                                market_value = prop.get("market_value", prop["price"])

                                # Find original property data to get down payment percent
                                original_prop_data = next((p for p in PROPERTIES if p["name"] == prop["name"]), None)
                                if original_prop_data:
                                    purchase_price = prop.get("purchase_price", original_prop_data["price"])
                                    down_payment_percent = original_prop_data["down_payment_percent"]
                                    loan_amount = purchase_price * (1 - down_payment_percent)

                                    # This is a simplification. A real simulation would track the remaining loan balance.
                                    equity = market_value - loan_amount
                                    portfolio["bank_balance"] += equity

                                    message_text = f"You sold {prop['name']} for ${market_value:,.0f}, gaining ${equity:,.0f} in equity."
                                else:
                                    # Fallback if property not found in PROPERTIES (should not happen)
                                    portfolio["bank_balance"] += market_value
                                    message_text = f"You sold {prop['name']} for ${market_value:,.0f}."

                                portfolio["real_estate"]["owned_properties"] = [p for p in portfolio["real_estate"]["owned_properties"] if p["name"] != prop["name"]]
                                if portfolio["real_estate"]["current_residence"] == prop["name"]:
                                    portfolio["real_estate"]["current_residence"] = "Living with Parents"
                                    portfolio["bills"] = {"rent_mortgage": 0, "utilities": 50, "living_expenses": 100}
                                message, message_color = message_text, GREEN
                            save_portfolio(portfolio)
                            message_timer = pygame.time.get_ticks() + 3000
                        y_pos_check += 120

        # --- Drawing ---
        virtual_screen.fill(WHITE)
        draw_text(virtual_screen, "Real Estate Market", title_font, BLACK, VIRTUAL_WIDTH // 2, 70)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10); draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)
        draw_text(virtual_screen, f"Bank: ${bank_balance:,.2f}", font, BLACK, VIRTUAL_WIDTH - 250, 20, False)

        draw_rounded_rect(virtual_screen, rent_tab_button, BLUE if active_tab == "For Rent" else GRAY, 10); draw_text(virtual_screen, "For Rent", font, BLACK, rent_tab_button.centerx, rent_tab_button.centery)
        draw_rounded_rect(virtual_screen, buy_tab_button, BLUE if active_tab == "For Sale" else GRAY, 10); draw_text(virtual_screen, "For Sale", font, BLACK, buy_tab_button.centerx, buy_tab_button.centery)
        draw_rounded_rect(virtual_screen, portfolio_tab_button, BLUE if active_tab == "Portfolio" else GRAY, 10); draw_text(virtual_screen, "My Portfolio", font, BLACK, portfolio_tab_button.centerx, portfolio_tab_button.centery)

        list_area = pygame.Rect(50, 170, 700, 350)
        virtual_screen.set_clip(list_area)
        y_pos_draw = list_area.y - scroll_y
        
        properties_to_show = []
        if active_tab == "Portfolio": properties_to_show = portfolio.get("real_estate", {}).get("owned_properties", [])
        else: properties_to_show = [p for p in PROPERTIES if p["status"] == active_tab]

        for prop in properties_to_show:
            item_rect = pygame.Rect(list_area.x + 10, y_pos_draw, list_area.w - 20, 100)
            draw_rounded_rect(virtual_screen, item_rect, WHITE, 15); pygame.draw.rect(virtual_screen, BLACK, item_rect, 2, 15)
            draw_text(virtual_screen, prop['name'], font, BLACK, item_rect.left + 20, item_rect.y + 20, False)
            
            action_text, btn_color = "", GRAY
            if active_tab == "For Rent":
                draw_text(virtual_screen, f"Rent: ${prop['rent']}/mo", small_font, BLACK, item_rect.left + 20, item_rect.y + 60, False)
                action_text, btn_color = "Rent", GREEN
            elif active_tab == "For Sale":
                price = prop['price']; down_payment = price * prop['down_payment_percent']
                draw_text(virtual_screen, f"Price: ${price:,.0f} (DP: ${down_payment:,.0f})", small_font, BLACK, item_rect.left + 20, item_rect.y + 60, False)
                action_text, btn_color = "Buy", GREEN if bank_balance >= down_payment else RED
            elif active_tab == "Portfolio":
                market_value = prop.get('market_value', prop['price'])
                draw_text(virtual_screen, f"Value: ${market_value:,.0f}", small_font, BLACK, item_rect.left + 20, item_rect.y + 60, False)
                action_text, btn_color = "Sell", RED

            action_button = pygame.Rect(600, y_pos_draw + 30, 120, 40)
            draw_rounded_rect(virtual_screen, action_button, btn_color, 10); draw_text(virtual_screen, action_text, font, BLACK, action_button.centerx, action_button.centery)
            y_pos_draw += 120
        virtual_screen.set_clip(None)

        draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)
        if message and pygame.time.get_ticks() < message_timer: draw_text(virtual_screen, message, small_font, message_color, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 30)

        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    housing_main()
