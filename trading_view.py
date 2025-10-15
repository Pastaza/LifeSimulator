import pygame
import sys
import os
import random
import math
import json
import numpy as np
from collections import deque
import news as news_generator

# Initialize Pygame
pygame.init()

# --- Screen and Scaling Setup ---
VIRTUAL_WIDTH = 800
VIRTUAL_HEIGHT = 600
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
pygame.display.set_caption("Trading")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); RED = (255, 0, 0); GRAY = (200, 200, 200); BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# --- Data Management and Asset Info ---
PORTFOLIO_FILE = "portfolio.json"
ASSETS = {
    "crypto": ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX"],
    "stocks": ["AAPL", "GOOG", "TSLA", "AMZN", "MSFT", "NVDA", "META"],
    "forex": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD"],
    "indices": ["SPY", "QQQ", "DIA"],
    "bonds": ["2Y-Yield", "5Y-Yield", "10Y-Yield"]
}
asset_prices = {}

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f: return json.load(f)
    return {"bank_balance": 1000.0, "cash_on_hand": 100.0, "assets": {}, "realized_pnl": {}}

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w') as f: json.dump(data, f, indent=2)

# --- Price Simulation ---
def generate_historical_prices(start_price, days, volatility):
    prices = [start_price]
    for _ in range(days - 1):
        dt = 1/365; drift = 0.05 * dt; shock = volatility * np.random.normal(0, math.sqrt(dt))
        prices.append(prices[-1] * math.exp(drift + shock))
    return prices

def prices_to_candles(prices):
    candles = []
    for i in range(0, len(prices) - 4, 4):
        segment = prices[i:i+4]
        candles.append({'open': segment[0], 'high': max(segment), 'low': min(segment), 'close': segment[-1]})
    return candles

def initialize_prices():
    for asset_type, asset_list in ASSETS.items():
        for asset_id in asset_list:
            if asset_id not in asset_prices:
                volatility = 0.3; start_price = 100
                if asset_type == 'crypto': volatility = 0.9; start_price = random.uniform(10, 45000)
                elif asset_type == 'stocks': volatility = 0.5; start_price = random.uniform(100, 500)
                elif asset_type == 'forex': volatility = 0.1; start_price = random.uniform(0.5, 150)
                elif asset_type == 'indices': volatility = 0.2; start_price = random.uniform(300, 500)
                elif asset_type == 'bonds': volatility = 0.05; start_price = random.uniform(3.5, 5.0)
                daily_prices = generate_historical_prices(start_price, 180 * 4, volatility)
                price_history = prices_to_candles(daily_prices)
                asset_prices[asset_id] = {
                    'current_price': price_history[-1]['close'], 'price_history': price_history,
                    'open': price_history[-1]['close'], 'high': price_history[-1]['close'], 'low': price_history[-1]['close'],
                    'volatility': volatility, 'last_update': pygame.time.get_ticks(), 'last_candle': pygame.time.get_ticks()
                }
initialize_prices()

# --- UI & Main ---
def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y)) if center else textobj.get_rect(topleft=(x, y))
    surface.blit(textobj, textrect)

def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def trading_main(is_fullscreen_initial=False):
    global screen, virtual_screen
    active_asset_type, active_asset_id = "crypto", ASSETS["crypto"][0]
    view_offset, is_dragging = 0, False
    input_text, input_active = "", False
    is_fullscreen = is_fullscreen_initial
    candles_on_screen = 50
    asset_type_scroll_y, asset_id_scroll_y = 0, 0

    buy_button = pygame.Rect(50, 500, 150, 50); sell_button = pygame.Rect(250, 500, 150, 50)
    back_button = pygame.Rect(600, 550, 150, 30); input_box = pygame.Rect(50, 440, 250, 50)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)
    asset_type_area = pygame.Rect(670, 80, 120, 180)
    asset_id_area = pygame.Rect(670, 270, 120, 220)

    running = True
    while running:
        portfolio = load_portfolio()
        current_time = pygame.time.get_ticks()
        chart_area = pygame.Rect(50, 150, 600, 250)
        scaled_mouse_pos = (pygame.mouse.get_pos()[0] * (VIRTUAL_WIDTH / screen.get_width()), pygame.mouse.get_pos()[1] * (VIRTUAL_HEIGHT / screen.get_height()))

        # --- P&L Calculation ---
        asset_data = portfolio["assets"].get(active_asset_type, {}).get(active_asset_id, {})
        quantity = asset_data.get("quantity", 0)
        total_cost_basis = asset_data.get("total_cost_basis", 0)
        current_price = asset_prices[active_asset_id]['current_price']
        unrealized_pnl = (quantity * current_price) - total_cost_basis if quantity > 0 else 0
        realized_pnl = portfolio["realized_pnl"].get(active_asset_type, 0.0)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.MOUSEWHEEL:
                if asset_type_area.collidepoint(scaled_mouse_pos): asset_type_scroll_y = max(0, min(asset_type_scroll_y - event.y * 20, len(ASSETS) * 50 - asset_type_area.h))
                elif asset_id_area.collidepoint(scaled_mouse_pos): asset_id_scroll_y = max(0, min(asset_id_scroll_y - event.y * 20, len(ASSETS[active_asset_type]) * 50 - asset_id_area.h))
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
                input_active = input_box.collidepoint(mouse_pos)
                type_y = asset_type_area.y - asset_type_scroll_y
                for type_name in ASSETS.keys():
                    if pygame.Rect(asset_type_area.x, type_y, asset_type_area.w, 40).collidepoint(mouse_pos): active_asset_type, active_asset_id = type_name, ASSETS[type_name][0]; asset_id_scroll_y = 0; view_offset = 0
                    type_y += 50
                id_y = asset_id_area.y - asset_id_scroll_y
                for id_name in ASSETS[active_asset_type]:
                    if pygame.Rect(asset_id_area.x, id_y, asset_id_area.w, 40).collidepoint(mouse_pos): active_asset_id = id_name; view_offset = 0
                    id_y += 50
                if buy_button.collidepoint(mouse_pos):
                    try:
                        amount = float(input_text)
                        cost = amount * asset_prices[active_asset_id]['current_price']
                        if amount > 0 and portfolio['bank_balance'] >= cost:
                            portfolio['bank_balance'] -= cost
                            asset_type_dict = portfolio['assets'].setdefault(active_asset_type, {})
                            asset = asset_type_dict.setdefault(active_asset_id, {'quantity': 0, 'total_cost_basis': 0})
                            asset['total_cost_basis'] += cost
                            asset['quantity'] += amount
                            save_portfolio(portfolio); input_text = ""
                    except ValueError: pass
                if sell_button.collidepoint(mouse_pos):
                    try:
                        amount = float(input_text)
                        asset_type_dict = portfolio['assets'].get(active_asset_type, {})
                        asset = asset_type_dict.get(active_asset_id)
                        if asset and amount > 0 and asset['quantity'] >= amount:
                            avg_cost_price = asset['total_cost_basis'] / asset['quantity']
                            pnl = (amount * asset_prices[active_asset_id]['current_price']) - (amount * avg_cost_price)

                            realized_pnl_dict = portfolio.setdefault('realized_pnl', {})
                            realized_pnl_dict[active_asset_type] = realized_pnl_dict.get(active_asset_type, 0) + pnl

                            asset['total_cost_basis'] -= amount * avg_cost_price
                            asset['quantity'] -= amount

                            if asset['quantity'] < 1e-9:
                                del asset_type_dict[active_asset_id]

                            portfolio['bank_balance'] += amount * asset_prices[active_asset_id]['current_price']
                            save_portfolio(portfolio); input_text = ""
                    except (ValueError, ZeroDivisionError): pass
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() or (event.unicode == '.' and '.' not in input_text):
                    input_text += event.unicode

        # --- Price Updates ---
        news_event = news_generator.get_market_news(active_asset_type, active_asset_id)
        for asset_id, price_data in asset_prices.items():
            if current_time - price_data['last_update'] > 1000:
                news_drift = 0
                if news_event and (news_event['target_asset'] == 'all' or news_event['target_asset'] == asset_id):
                    news_drift = news_event['magnitude'] * (1/365)
                dt = 1/365; shock = price_data['volatility'] * np.random.normal(0, math.sqrt(dt))
                price_data['current_price'] *= math.exp(news_drift + shock)
                price_data['last_update'] = current_time

        # --- Drawing ---
        virtual_screen.fill(WHITE)
        draw_text(virtual_screen, f"Bank: ${portfolio['bank_balance']:.2f}", small_font, BLACK, 150, 20, False)
        draw_text(virtual_screen, f"Cash: ${portfolio['cash_on_hand']:.2f}", small_font, BLACK, 150, 50, False)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)
        if news_event: draw_text(virtual_screen, news_event['headline'], small_font, RED, VIRTUAL_WIDTH//2, 20)
        
        draw_text(virtual_screen, f"Price: ${current_price:.2f}", font, BLACK, VIRTUAL_WIDTH // 2, 50)
        draw_text(virtual_screen, f"Qty: {quantity:.6f}", small_font, BLACK, 20, 80, False)
        unrealized_color = GREEN if unrealized_pnl >= 0 else RED
        draw_text(virtual_screen, f"Unrealized: ${unrealized_pnl:.2f}", small_font, unrealized_color, 20, 100, False)
        realized_color = GREEN if realized_pnl >= 0 else RED
        draw_text(virtual_screen, f"Realized: ${realized_pnl:.2f}", small_font, realized_color, 20, 120, False)

        pygame.draw.rect(virtual_screen, GRAY, chart_area, 1)
        price_history = asset_prices[active_asset_id]['price_history']
        end_index = len(price_history) - view_offset
        start_index = max(0, end_index - candles_on_screen)
        visible_candles = price_history[start_index:end_index]
        if visible_candles:
            max_p, min_p = max(c['high'] for c in visible_candles), min(c['low'] for c in visible_candles)
            price_range = max_p - min_p if max_p > min_p else 1
            candle_w = chart_area.width / (len(visible_candles) or 1)
            for i, candle in enumerate(visible_candles):
                x = chart_area.left + i * candle_w
                open_y = chart_area.bottom - ((candle['open'] - min_p) / price_range * chart_area.height)
                close_y = chart_area.bottom - ((candle['close'] - min_p) / price_range * chart_area.height)
                high_y = chart_area.bottom - ((candle['high'] - min_p) / price_range * chart_area.height)
                low_y = chart_area.bottom - ((candle['low'] - min_p) / price_range * chart_area.height)
                color = GREEN if candle['close'] >= candle['open'] else RED
                pygame.draw.line(virtual_screen, color, (x + candle_w / 2, high_y), (x + candle_w / 2, low_y))
                body_rect = pygame.Rect(x, min(open_y, close_y), candle_w, max(1, abs(open_y - close_y)))
                pygame.draw.rect(virtual_screen, color, body_rect)

        virtual_screen.set_clip(asset_type_area)
        type_y = asset_type_area.y - asset_type_scroll_y
        for type_name in ASSETS.keys():
            type_rect = pygame.Rect(asset_type_area.x, type_y, asset_type_area.w, 40)
            draw_rounded_rect(virtual_screen, type_rect, BLUE if type_name == active_asset_type else GRAY, 10)
            draw_text(virtual_screen, type_name.capitalize(), small_font, BLACK, type_rect.centerx, type_rect.centery)
            type_y += 50
        virtual_screen.set_clip(None)

        virtual_screen.set_clip(asset_id_area)
        id_y = asset_id_area.y - asset_id_scroll_y
        for id_name in ASSETS[active_asset_type]:
            id_rect = pygame.Rect(asset_id_area.x, id_y, asset_id_area.w, 40)
            draw_rounded_rect(virtual_screen, id_rect, BLUE if id_name == active_asset_id else GRAY, 10)
            draw_text(virtual_screen, id_name, small_font, BLACK, id_rect.centerx, id_rect.centery)
            id_y += 50
        virtual_screen.set_clip(None)

        draw_rounded_rect(virtual_screen, buy_button, GREEN, 15); draw_text(virtual_screen, "Buy", font, BLACK, buy_button.centerx, buy_button.centery)
        draw_rounded_rect(virtual_screen, sell_button, RED, 15); draw_text(virtual_screen, "Sell", font, BLACK, sell_button.centerx, sell_button.centery)
        draw_rounded_rect(virtual_screen, back_button, GRAY, 15); draw_text(virtual_screen, "Back", small_font, BLACK, back_button.centerx, back_button.centery)
        pygame.draw.rect(virtual_screen, BLACK if input_active else GRAY, input_box, 2, border_radius=15)
        draw_text(virtual_screen, input_text, font, BLACK, input_box.centerx, input_box.centery)

        # --- Scale and Update Real Screen ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    trading_main()