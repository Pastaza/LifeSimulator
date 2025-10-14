
import pygame
import sys
import os
import random
import math
import json
from collections import deque

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crypto Trading")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Data files
BALANCE_FILE = "/home/zach/Banking life sim/balance.txt"
CRYPTO_DATA_FILE = "/home/zach/Banking life sim/crypto_data.txt"

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

def load_crypto_data():
    if os.path.exists(CRYPTO_DATA_FILE):
        with open(CRYPTO_DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    return {"crypto_balance": 0.0, "total_cost_basis": 0.0, "realized_pnl": 0.0}

def save_crypto_data(data):
    with open(CRYPTO_DATA_FILE, 'w') as f:
        json.dump(data, f)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def crypto_main():
    balance = load_balance()
    crypto_data = load_crypto_data()
    crypto_balance = crypto_data["crypto_balance"]
    total_cost_basis = crypto_data["total_cost_basis"]
    realized_pnl = crypto_data["realized_pnl"]

    # Crypto data
    current_price = 50000.0
    price_history = [] # Use a list to store full history
    
    # Pre-fill price history
    _price = current_price
    for _ in range(200): # Start with more data for scrolling
        open_p = _price
        high_p = open_p * random.uniform(1, 1.02)
        low_p = open_p * random.uniform(0.98, 1)
        close_p = random.uniform(low_p, high_p)
        price_history.append({'open': open_p, 'high': high_p, 'low': low_p, 'close': close_p})
        _price = close_p

    # Initial candle
    open_price = price_history[-1]['close']
    high_price = open_price
    low_price = open_price
    
    last_minute_update_time = pygame.time.get_ticks()
    last_price_update_time = pygame.time.get_ticks()

    # Panning and dragging
    view_offset = 0
    is_dragging = False
    drag_start_x = 0
    initial_view_offset = 0
    candles_on_screen = 50

    # Buttons
    buy_button = pygame.Rect(50, 500, 150, 50)
    sell_button = pygame.Rect(250, 500, 150, 50)
    back_button = pygame.Rect(600, 550, 150, 30)
    
    input_box = pygame.Rect(50, 440, 250, 50)
    input_text = ""
    input_active = False

    running = True
    while running:
        screen.fill(WHITE)
        
        current_time = pygame.time.get_ticks()
        chart_area = pygame.Rect(50, 150, 650, 250)

        # Update candle every minute
        if current_time - last_minute_update_time > 60000:
            price_history.append({'open': open_price, 'high': high_price, 'low': low_price, 'close': current_price})
            
            # New candle
            open_price = current_price
            high_price = current_price
            low_price = current_price
            last_minute_update_time = current_time

        # Simulate price change every second
        if current_time - last_price_update_time > 1000:
            price_change = random.uniform(-0.02, 0.02)
            current_price *= (1 + price_change)
            if current_price > high_price:
                high_price = current_price
            if current_price < low_price:
                low_price = current_price
            last_price_update_time = current_time

        # --- P&L Calculation ---
        unrealized_pnl = (crypto_balance * current_price) - total_cost_basis if crypto_balance > 0 else 0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False
                elif chart_area.collidepoint(event.pos):
                    is_dragging = True
                    drag_start_x = event.pos[0]
                    initial_view_offset = view_offset
                elif input_box.collidepoint(event.pos):
                    input_active = not input_active
                else:
                    input_active = False

                if buy_button.collidepoint(event.pos):
                    try:
                        amount_crypto = float(input_text)
                        cost_usd = amount_crypto * current_price
                        if amount_crypto > 0 and balance >= cost_usd:
                            balance -= cost_usd
                            crypto_balance += amount_crypto
                            total_cost_basis += cost_usd
                            save_balance(balance)
                            save_crypto_data({"crypto_balance": crypto_balance, "total_cost_basis": total_cost_basis, "realized_pnl": realized_pnl})
                            input_text = ""
                    except ValueError:
                        pass
                
                if sell_button.collidepoint(event.pos):
                    try:
                        amount_crypto = float(input_text)
                        if amount_crypto > 0 and crypto_balance >= amount_crypto:
                            avg_cost_per_coin = total_cost_basis / crypto_balance if crypto_balance > 0 else 0
                            cost_of_sold_crypto = amount_crypto * avg_cost_per_coin
                            realized_pnl += (amount_crypto * current_price) - cost_of_sold_crypto
                            total_cost_basis -= cost_of_sold_crypto
                            crypto_balance -= amount_crypto
                            if crypto_balance < 1e-9:
                                crypto_balance = 0
                                total_cost_basis = 0
                            balance += amount_crypto * current_price
                            save_balance(balance)
                            save_crypto_data({"crypto_balance": crypto_balance, "total_cost_basis": total_cost_basis, "realized_pnl": realized_pnl})
                            input_text = ""
                    except ValueError:
                        pass

            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False

            if event.type == pygame.MOUSEMOTION and is_dragging:
                dx = event.pos[0] - drag_start_x
                candle_width = chart_area.width / (candles_on_screen + 1)
                candle_offset = int(dx // candle_width)
                view_offset = initial_view_offset - candle_offset
                # Clamp offset
                max_offset = len(price_history) - candles_on_screen
                if view_offset < 0:
                    view_offset = 0
                if view_offset > max_offset:
                    view_offset = max_offset

            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        # --- Drawing ---
        
        # Draw balance and crypto balance
        balance_text = font.render(f"Balance: ${balance:.2f}", True, BLACK)
        screen.blit(balance_text, (20, 20))
        crypto_balance_text = font.render(f"Crypto: {crypto_balance:.6f}", True, BLACK)
        screen.blit(crypto_balance_text, (20, 50))

        # Draw P&L
        unrealized_pnl_color = GREEN if unrealized_pnl >= 0 else RED
        unrealized_pnl_text = small_font.render(f"Unrealized P&L: ${unrealized_pnl:.2f}", True, unrealized_pnl_color)
        screen.blit(unrealized_pnl_text, (20, 80))
        realized_pnl_color = GREEN if realized_pnl >= 0 else RED
        realized_pnl_text = small_font.render(f"Realized P&L: ${realized_pnl:.2f}", True, realized_pnl_color)
        screen.blit(realized_pnl_text, (20, 100))

        # Draw current price
        price_text = font.render(f"Price: ${current_price:.2f}", True, BLACK)
        screen.blit(price_text, (SCREEN_WIDTH - price_text.get_width() - 20, 20))

        # Draw candles
        pygame.draw.rect(screen, GRAY, chart_area, 1)

        # Determine visible candles
        end_index = len(price_history) - view_offset
        start_index = max(0, end_index - candles_on_screen)
        visible_candles = price_history[start_index:end_index]

        if visible_candles:
            candles_to_scale = visible_candles
            if view_offset == 0:
                candles_to_scale = visible_candles + [{'open': open_price, 'high': high_price, 'low': low_price, 'close': current_price}]
            
            max_price = max(c['high'] for c in candles_to_scale)
            min_price = min(c['low'] for c in candles_to_scale)
            price_range = max_price - min_price if max_price > min_price else 1

            candle_width = chart_area.width / (len(visible_candles) + (1 if view_offset == 0 else 0))
            
            # Draw historical candles
            for i, candle in enumerate(visible_candles):
                x = chart_area.left + i * candle_width
                open_y = chart_area.bottom - ((candle['open'] - min_price) / price_range * chart_area.height)
                close_y = chart_area.bottom - ((candle['close'] - min_price) / price_range * chart_area.height)
                high_y = chart_area.bottom - ((candle['high'] - min_price) / price_range * chart_area.height)
                low_y = chart_area.bottom - ((candle['low'] - min_price) / price_range * chart_area.height)
                
                color = GREEN if candle['close'] >= candle['open'] else RED
                pygame.draw.line(screen, color, (x + candle_width / 2, high_y), (x + candle_width / 2, low_y))
                body_height = abs(open_y - close_y)
                if body_height < 1: body_height = 1
                body_rect = pygame.Rect(x, min(open_y, close_y), candle_width, body_height)
                pygame.draw.rect(screen, color, body_rect)

            # Draw live candle only if in live view
            if view_offset == 0:
                live_candle_x = chart_area.left + len(visible_candles) * candle_width
                live_open_y = chart_area.bottom - ((open_price - min_price) / price_range * chart_area.height)
                live_close_y = chart_area.bottom - ((current_price - min_price) / price_range * chart_area.height)
                live_high_y = chart_area.bottom - ((high_price - min_price) / price_range * chart_area.height)
                live_low_y = chart_area.bottom - ((low_price - min_price) / price_range * chart_area.height)
                live_color = GREEN if current_price >= open_price else RED
                pygame.draw.line(screen, live_color, (live_candle_x + candle_width / 2, live_high_y), (live_candle_x + candle_width / 2, live_low_y))
                live_body_height = abs(live_open_y - live_close_y)
                if live_body_height < 1: live_body_height = 1
                live_body_rect = pygame.Rect(live_candle_x, min(live_open_y, live_close_y), candle_width, live_body_height)
                pygame.draw.rect(screen, live_color, live_body_rect)

            # Draw price scale
            scale_area = pygame.Rect(chart_area.right, chart_area.top, 50, chart_area.height)
            start_price = math.ceil(min_price / 500) * 500
            for price_level in range(start_price, int(max_price) + 500, 500):
                y = chart_area.bottom - ((price_level - min_price) / price_range * chart_area.height)
                if chart_area.top < y < chart_area.bottom:
                    pygame.draw.line(screen, GRAY, (chart_area.right - 5, y), (chart_area.right, y))
                    scale_text = small_font.render(f"${price_level}", True, BLACK)
                    screen.blit(scale_text, (chart_area.right + 5, y - scale_text.get_height()/2))

        draw_rounded_rect(screen, buy_button, GREEN, 15)
        draw_text("Buy", font, BLACK, screen, buy_button.centerx, buy_button.centery)
        draw_rounded_rect(screen, sell_button, RED, 15)
        draw_text("Sell", font, BLACK, screen, sell_button.centerx, sell_button.centery)
        draw_rounded_rect(screen, back_button, GRAY, 15)
        draw_text("Back", small_font, BLACK, screen, back_button.centerx, back_button.centery)
        
        draw_text("Amount:", small_font, BLACK, screen, input_box.left - 40, input_box.centery)
        pygame.draw.rect(screen, BLACK if input_active else GRAY, input_box, 2, border_radius=15)
        draw_text(input_text, font, BLACK, screen, input_box.centerx, input_box.centery)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == "__main__":
    crypto_main()
