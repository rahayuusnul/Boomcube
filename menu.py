#menu.py

import pygame
import os

BLACK = (0,0,0)
ICON_CACHE = {}

def load_icon(name, size=(42,42)):
    if name in ICON_CACHE:
        return ICON_CACHE[name]

    path = os.path.join("assets", name)
    if not os.path.exists(path):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (255,0,0), (0,0,size[0],size[1]), 2)
        ICON_CACHE[name] = surf
        return surf

    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.smoothscale(img, size)
    ICON_CACHE[name] = img
    return img

def draw_center_button(screen, rect, color, outline, icon, text, font):
    pygame.draw.rect(screen, color, rect, border_radius=20)
    pygame.draw.rect(screen, outline, rect, 3, border_radius=20)
    icon_size = icon.get_width()
    icon_x = rect.x + 40
    icon_y = rect.centery - icon_size // 2
    screen.blit(icon, (icon_x, icon_y))
    label = font.render(text, True, BLACK)
    text_x = rect.centerx - label.get_width() // 2 + 10
    text_y = rect.centery - label.get_height() // 2
    screen.blit(label, (text_x, text_y))

def draw_menu(screen, title_font, subtitle_font, button_font, small_font):
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    screen.fill((30,120,255))
    LOGO = load_icon("logo1.png", (360,250))
    screen.blit(LOGO, (WIDTH//2 - LOGO.get_width()//2, 120))
    MEDAL = load_icon("icon_medali.png", (80,80))
    screen.blit(MEDAL, (WIDTH - 90, 20))
    btn_w, btn_h = 300, 80
    gap = 26
    bx = WIDTH//2 - btn_w//2
    start_y = 120 + LOGO.get_height() + 60
    ICON_MAP = load_icon("icon_map.png")
    ICON_LOOP = load_icon("icon_loop.png")
    ICON_GAMES = load_icon("icon_games.png")
    adv = pygame.Rect(bx, start_y, btn_w, btn_h)
    draw_center_button(screen, adv, (255,150,50), BLACK, ICON_MAP, "Adventure", button_font)
    cls = pygame.Rect(bx, start_y + btn_h + gap, btn_w, btn_h)
    draw_center_button(screen, cls, (40,200,170), BLACK, ICON_LOOP, "Classic", button_font)
    mg = pygame.Rect(bx, start_y + 2*(btn_h + gap), btn_w, btn_h)
    draw_center_button(screen, mg, (60,160,255), BLACK, ICON_GAMES, "More Games", button_font)
    return [
        ("ADVENTURE", adv),
        ("CLASSIC", cls),
        ("MORE", mg)
    ]
