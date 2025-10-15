
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
pygame.display.set_caption("Job Market")

# Colors
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREEN = (0, 255, 0); GRAY = (200, 200, 200); RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- Data and Utility Functions ---
PORTFOLIO_FILE = "portfolio.json"
JOBS = {
    "Entry Level": [
        {"title": "Fast Food Worker", "salary": 30000, "education_req": None},
        {"title": "Retail Assistant", "salary": 32000, "education_req": None},
    ],
    "Mid Level": [
        {"title": "Office Administrator", "salary": 45000, "education_req": "Business Certificate"},
        {"title": "Junior Developer", "salary": 60000, "education_req": "Programming Bootcamp"},
    ],
    "High Level": [
        {"title": "Accountant", "salary": 80000, "education_req": "Finance Degree"},
        {"title": "Senior Developer", "salary": 120000, "education_req": "Computer Science Degree"},
    ],
    "Executive": [
        {"title": "Chief Financial Officer", "salary": 250000, "education_req": "Finance Degree"},
        {"title": "Chief Technology Officer", "salary": 300000, "education_req": "Computer Science Degree"},
    ]
}

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
def jobs_main(is_fullscreen_initial=False):
    global screen, virtual_screen
    is_fullscreen = is_fullscreen_initial
    scroll_y = 0

    back_button = pygame.Rect(20, 550, 100, 30)
    fullscreen_button = pygame.Rect(10, 10, 130, 30)

    # Calculate total content height for scrolling limits
    content_height = 150
    for category, job_list in JOBS.items():
        content_height += 40 # Category title
        content_height += len(job_list) * 60 # Job entries
        content_height += 20 # Padding

    running = True
    while running:
        portfolio = load_portfolio()
        user_education = portfolio.get("education", [])
        current_job = portfolio.get("current_job")

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return is_fullscreen, True
            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 20 # Scroll speed
                max_scroll = content_height - VIRTUAL_HEIGHT
                if max_scroll < 0: max_scroll = 0
                scroll_y = max(0, min(scroll_y, max_scroll))

            if event.type == pygame.MOUSEBUTTONDOWN:
                real_screen_size = screen.get_size()
                scale_x = VIRTUAL_WIDTH / real_screen_size[0]
                scale_y = VIRTUAL_HEIGHT / real_screen_size[1]
                # Adjust mouse click position for scrolling
                mouse_pos = (event.pos[0] * scale_x, event.pos[1] * scale_y + scroll_y)

                if pygame.Rect(fullscreen_button.x, fullscreen_button.y, fullscreen_button.w, fullscreen_button.h).collidepoint(event.pos[0] * scale_x, event.pos[1] * scale_y):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                elif pygame.Rect(back_button.x, back_button.y, back_button.w, back_button.h).collidepoint(event.pos[0] * scale_x, event.pos[1] * scale_y):
                    running = False
                else:
                    y_pos_check = 150
                    for category, job_list in JOBS.items():
                        y_pos_check += 40
                        for job in job_list:
                            job_rect = pygame.Rect(100, y_pos_check, 600, 50)
                            if job_rect.collidepoint(mouse_pos):
                                has_req = job["education_req"] is None or job["education_req"] in user_education
                                if has_req:
                                    portfolio["current_job"] = job
                                    save_portfolio(portfolio)
                            y_pos_check += 60
                        y_pos_check += 20

        # --- Drawing (on virtual_screen) ---
        virtual_screen.fill(WHITE)
        
        # Draw scrolling content
        y_pos_draw = 150 - scroll_y
        for category, job_list in JOBS.items():
            draw_text(virtual_screen, category, font, BLACK, 100, y_pos_draw, center=False)
            y_pos_draw += 40
            for job in job_list:
                rect = pygame.Rect(100, y_pos_draw, 600, 50)
                has_req = job["education_req"] is None or job["education_req"] in user_education
                color = GRAY if not has_req else (GREEN if current_job and current_job['title'] == job['title'] else WHITE)
                pygame.draw.rect(virtual_screen, BLACK, rect, 2, border_radius=10)
                pygame.draw.rect(virtual_screen, color, rect.inflate(-4, -4), border_radius=8)
                draw_text(virtual_screen, job['title'], font, BLACK, rect.left + 150, rect.centery, center=False)
                draw_text(virtual_screen, f"${job['salary']:,}/yr", font, BLACK, rect.left + 400, rect.centery, center=False)
                if job["education_req"]:
                    draw_text(virtual_screen, job["education_req"], small_font, GREEN if has_req else RED, rect.left + 15, rect.top - 20, center=False)
                y_pos_draw += 60
            y_pos_draw += 20

        # --- Fixed UI Elements (drawn over scrolling content) ---
        # Header and Footer
        header_bg = pygame.Rect(0, 0, VIRTUAL_WIDTH, 120)
        footer_bg = pygame.Rect(0, VIRTUAL_HEIGHT - 70, VIRTUAL_WIDTH, 70)
        pygame.draw.rect(virtual_screen, WHITE, header_bg)
        pygame.draw.rect(virtual_screen, WHITE, footer_bg)

        draw_text(virtual_screen, "Job Market", title_font, BLACK, VIRTUAL_WIDTH // 2, 70)
        draw_rounded_rect(virtual_screen, fullscreen_button, GRAY, 10)
        draw_text(virtual_screen, "Fullscreen" if not is_fullscreen else "Windowed", small_font, BLACK, fullscreen_button.centerx, fullscreen_button.centery)
        if current_job:
            draw_text(virtual_screen, f"Current: {current_job['title']}", small_font, BLACK, VIRTUAL_WIDTH - 150, 20, center=False)
        else:
            draw_text(virtual_screen, "Current: Unemployed", small_font, BLACK, VIRTUAL_WIDTH - 200, 20, center=False)
        
        draw_rounded_rect(virtual_screen, back_button, GRAY, 15)
        draw_text(virtual_screen, "Back", font, BLACK, back_button.centerx, back_button.centery)

        # --- Scale and Update Real Screen ---
        scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return is_fullscreen, False

if __name__ == "__main__":
    jobs_main()
