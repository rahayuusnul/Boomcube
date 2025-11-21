# main.py
import pygame
import sys
import os
import random
from menu import draw_menu
from adventure_menu import AdventureMenu
from grid import Grid, GRID_SIZE, CELL_SIZE
from shapes import get_n_shapes
from adventure import LEVELS, start_level

pygame.init()
pygame.font.init()

# ------------------ WINDOW ------------------
WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast – Classic Final")
clock = pygame.time.Clock()

# ------------------ FONTS ------------------
title_font = pygame.font.SysFont("Arial", 64, bold=True)
button_font = pygame.font.SysFont("Arial", 28, bold=True)
small_font = pygame.font.SysFont("Arial", 18)

# ------------------ LAYOUT ------------------
GRID_OFFSET_X = WIDTH//2 - (GRID_SIZE*CELL_SIZE)//2
GRID_OFFSET_Y = 130

# ------------------ STATE ------------------
game_state = "menu"  # menu | adventure_menu | playing | gameover | adventure

grid = None
upcoming = []
selected_idx = None
selected_shape = None
selected_color = None
dragging = False

score = 0
praise_text = None
praise_timer = 0

bg_color = (210,180,240)
fallback_block_color = (170,140,210)
HIGH_SCORE_FILE = "highscore.txt"

current_level = 0
adventure_state = None

# ------------------ HIGH SCORE ------------------
def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
    except:
        pass
    return 0

def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(int(value)))
    except:
        pass

high_score = load_high_score()

# ------------------ RANDOM COLOR ------------------
def rand_color():
    return (
        random.randint(80,255),
        random.randint(80,255),
        random.randint(80,255)
    )

# ------------------ RESET GAME ------------------
def reset_game_state():
    global grid, upcoming, selected_idx, selected_shape, selected_color, dragging
    global score, praise_text, praise_timer

    grid = Grid(GRID_OFFSET_X, GRID_OFFSET_Y)
    upcoming.clear()
    for s in get_n_shapes(3):
        upcoming.append({"shape": s, "color": rand_color()})

    selected_idx = None
    selected_shape = None
    selected_color = None
    dragging = False
    score = 0
    praise_text = None
    praise_timer = 0

# ------------------ UPCOMING PANEL ------------------
def draw_upcoming_panel(surf):
    panel_h = 180
    panel_rect = pygame.Rect(0, HEIGHT - panel_h, WIDTH, panel_h)
    panel_bg = tuple(max(0, min(255, c+10)) for c in bg_color)
    pygame.draw.rect(surf, panel_bg, panel_rect)

    gap = 20
    preview_w = 90
    start_x = WIDTH//2 - (preview_w*3 + gap*2)//2
    y = panel_rect.y + 20

    for i in range(3):
        box = pygame.Rect(start_x + i*(preview_w+gap), y, preview_w, preview_w)
        pygame.draw.rect(surf, tuple(max(0,min(255,c+20)) for c in bg_color), box, border_radius=10)
        pygame.draw.rect(surf, (120,90,140), box, 2, border_radius=10)

        entry = upcoming[i]
        if entry:
            s = entry["shape"]
            col = entry["color"]
            minx = min(pt[0] for pt in s)
            miny = min(pt[1] for pt in s)
            ext_w = max(pt[0] for pt in s) - minx + 1
            ext_h = max(pt[1] for pt in s) - miny + 1
            cell_preview = min(preview_w // max(ext_w, ext_h), preview_w // 3)
            base_x = box.x + (preview_w - cell_preview*ext_w)//2
            base_y = box.y + (preview_w - cell_preview*ext_h)//2
            for sx, sy in s:
                rx = base_x + (sx - minx)*cell_preview
                ry = base_y + (sy - miny)*cell_preview
                r = pygame.Rect(rx+6, ry+6, cell_preview-12, cell_preview-12)
                pygame.draw.rect(surf, col, r, border_radius=6)
                pygame.draw.rect(surf, (110,90,130), r, 2, border_radius=6)

        label = small_font.render("Used" if entry is None else "Pick", True, (90,70,110))
        surf.blit(label, (box.x + 6, box.y + preview_w + 6))

# ------------------ SNAPPED PREVIEW ------------------
def draw_snapped_preview(surf, shape, color, mx, my):
    if mx < GRID_OFFSET_X or my < GRID_OFFSET_Y:
        return
    minx = min(pt[0] for pt in shape)
    miny = min(pt[1] for pt in shape)
    gx = (mx - GRID_OFFSET_X) // CELL_SIZE - minx
    gy = (my - GRID_OFFSET_Y) // CELL_SIZE - miny
    px = GRID_OFFSET_X + gx * CELL_SIZE
    py = GRID_OFFSET_Y + gy * CELL_SIZE
    for sx, sy in shape:
        r = pygame.Rect(px + sx*CELL_SIZE + 6, py + sy*CELL_SIZE + 6, CELL_SIZE - 12, CELL_SIZE - 12)
        pygame.draw.rect(surf, color, r, border_radius=8)
        pygame.draw.rect(surf, (110,90,130), r, 2, border_radius=8)

# ------------------ LOAD ICONS ------------------
try:
    icon_out = pygame.image.load("assets/out.png").convert_alpha()
    icon_start = pygame.image.load("assets/start.png").convert_alpha()
except:
    icon_out = pygame.Surface((32,32), pygame.SRCALPHA)
    pygame.draw.rect(icon_out, (120,120,120), icon_out.get_rect(), 2)
    icon_start = icon_out.copy()

try:
    trophy_img = pygame.image.load("assets/winner.png").convert_alpha()
except:
    trophy_img = pygame.Surface((1,1), pygame.SRCALPHA)

# ------------------ BACK BUTTON HELPER ------------------
def draw_back_button(surf, x=10, y=10, icon=icon_out, size=26):
    rect = pygame.Rect(x, y, 40, 40)
    pygame.draw.rect(surf, (255,255,255), rect, border_radius=8)
    pygame.draw.rect(surf, (180,160,200), rect, 2, border_radius=8)
    surf.blit(pygame.transform.smoothscale(icon, (size,size)),
              (rect.centerx - size//2, rect.centery - size//2))
    return rect

# ------------------ CAN PLACE ANY SHAPE ------------------
def can_place_any_shape():
    for s_entry in upcoming:
        if not s_entry: 
            continue
        s = s_entry["shape"]
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid.can_place(s, x, y):
                    return True
    return False

# ------------------ DRAW GAME OVER ------------------
def draw_game_over(screen, score, high_score, note=None):
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,140))
    screen.blit(overlay, (0,0))

    box_w, box_h = 420, 340
    box_x, box_y = WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2
    pygame.draw.rect(screen, (255,255,255), (box_x, box_y, box_w, box_h), border_radius=22)
    pygame.draw.rect(screen, (0,0,0), (box_x, box_y, box_w, box_h), 4, border_radius=22)

    is_best = (score >= high_score and score > 0)
    title_text = "BEST SCORE!" if is_best else "GAME OVER"
    title_col = (255,200,50) if is_best else (0,0,0)
    screen.blit(title_font.render(title_text, True, title_col),
                (box_x + box_w//2 - title_font.size(title_text)[0]//2, box_y + 12))

    # trophy
    content_y = box_y + 80
    if trophy_img.get_width() > 1:
        trophy_w, trophy_h = 120, 120
        trophy_s = pygame.transform.smoothscale(trophy_img, (trophy_w, trophy_h))
        tx, ty = box_x + box_w//2 - trophy_w//2, box_y + 82
        screen.blit(trophy_s, (tx, ty))
        content_y = ty + trophy_h + 10

    # score
    screen.blit(button_font.render(f"Score: {score}", True, (0,0,0)),
                (box_x + box_w//2 - button_font.size(f"Score: {score}")[0]//2, content_y))
    screen.blit(button_font.render(f"Best: {high_score}", True, (0,0,0)),
                (box_x + box_w//2 - button_font.size(f"Best: {high_score}")[0]//2, content_y+46))
    if note:
        screen.blit(small_font.render(note, True, (0,0,0)),
                    (box_x + box_w//2 - small_font.size(note)[0]//2, content_y+96))

    # buttons
    btn_w, btn_h, gap_x = 120, 54, 30
    btn_y = box_y + box_h - btn_h - 22
    back_rect = pygame.Rect(box_x + gap_x, btn_y, btn_w, btn_h)
    restart_rect = pygame.Rect(box_x + box_w - btn_w - gap_x, btn_y, btn_w, btn_h)

    for rect in [back_rect, restart_rect]:
        pygame.draw.rect(screen, (240,240,240), rect, border_radius=16)
        pygame.draw.rect(screen, (0,0,0), rect, 3, border_radius=16)

    icon_size = 36
    screen.blit(pygame.transform.smoothscale(icon_out, (icon_size, icon_size)),
                (back_rect.centerx - icon_size//2, back_rect.centery - icon_size//2))
    screen.blit(pygame.transform.smoothscale(icon_start, (icon_size, icon_size)),
                (restart_rect.centerx - icon_size//2, restart_rect.centery - icon_size//2))

    return back_rect, restart_rect

# ------------------ ADVENTURE MENU ------------------
adventure_menu = AdventureMenu()

def start_adventure_level(idx):
    global current_level, adventure_state, score
    current_level = idx
    reset_game_state()
    adventure_state = start_level(LEVELS[current_level], grid)
    score = 0

def advance_adventure_level():
    global current_level, adventure_state, game_state
    current_level += 1
    if current_level >= len(LEVELS):
        game_state = "gameover"
        return
    start_adventure_level(current_level)

# ------------------ INIT ------------------
reset_game_state()

# ------------------ MAIN LOOP ------------------
while True:
    dt = clock.tick(60)/1000.0
    mx,my = pygame.mouse.get_pos()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            save_high_score(max(score, high_score))
            pygame.quit()
            sys.exit()

        # ------------------ MOUSE BUTTON DOWN ------------------
        if ev.type == pygame.MOUSEBUTTONDOWN:
            picked = False
            # ---- MENU ----
            if game_state == "menu":
                btns = draw_menu(screen, title_font, None, button_font, small_font)
                for name, rect in btns:
                    if rect.collidepoint(mx,my):
                        if name == "CLASSIC":
                            reset_game_state()
                            game_state = "playing"
                        elif name == "ADVENTURE":
                            game_state = "adventure_menu"

            # ---- ADVENTURE MENU ----
            elif game_state == "adventure_menu":
                lv = adventure_menu.click((mx,my))
                if lv:
                    idx = max(0, lv-1)
                    if idx < len(LEVELS):
                        start_adventure_level(idx)
                        game_state = "adventure"
                back_rect_top = pygame.Rect(10, 10, 40, 40)
                if back_rect_top.collidepoint(mx,my):
                    game_state = "menu"

            # ---- PLAYING / ADVENTURE ----
            elif game_state in ["playing", "adventure"]:
                panel_h, preview_w, gap = 180, 90, 20
                start_x, y = WIDTH//2 - (preview_w*3 + gap*2)//2, HEIGHT-panel_h+20
                for i in range(3):
                    box = pygame.Rect(start_x + i*(preview_w+gap), y, preview_w, preview_w)
                    if box.collidepoint(mx,my) and upcoming[i]:
                        selected_idx = i
                        selected_shape = upcoming[i]["shape"]
                        selected_color = upcoming[i]["color"]
                        dragging = True
                        picked = True
                        break

                back_rect_top = pygame.Rect(10, 10, 40, 40)
                if back_rect_top.collidepoint(mx,my):
                    if game_state == "adventure":
                        game_state = "adventure_menu"
                        adventure_state = None
                    else:
                        game_state = "menu"
                    dragging = False
                    selected_shape = None
                    selected_idx = None

                if not picked:
                    dragging = False
                    selected_shape = None
                    selected_color = None
                    selected_idx = None

        # ------------------ MOUSE BUTTON UP ------------------
        if ev.type == pygame.MOUSEBUTTONUP and dragging and selected_shape:
            minx = min(pt[0] for pt in selected_shape)
            miny = min(pt[1] for pt in selected_shape)
            gx = (mx - GRID_OFFSET_X)//CELL_SIZE - minx
            gy = (my - GRID_OFFSET_Y)//CELL_SIZE - miny
            if grid.can_place(selected_shape, gx, gy):
                grid.place(selected_shape, gx, gy, selected_color)
                score += len(selected_shape)
                cleared_count, _ = grid.clear_full_lines()
                if cleared_count>0: score += cleared_count*50

                # consume shape
                upcoming[selected_idx] = None
                selected_shape = None
                selected_color = None
                selected_idx = None
                dragging = False

                if all(s is None for s in upcoming):
                    upcoming.clear()
                    for s in get_n_shapes(3):
                        upcoming.append({"shape": s, "color": rand_color()})

                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

                # adventure completion
                if adventure_state:
                    mode = adventure_state.get("mode")
                    completed = False
                    if mode=="score" and score >= adventure_state.get("target",999999):
                        completed = True
                    elif mode=="match":
                        req = adventure_state.get("shape_required")
                        if req and grid.contains_shape(req):
                            completed = True
                    if completed:
                        adventure_menu.unlock_next_level(current_level)
                        advance_adventure_level()

    # ------------------ TIMER ------------------
    if game_state=="adventure" and adventure_state and adventure_state.get("mode")=="timer":
        adventure_state["timer"] = max(0, adventure_state["timer"]-dt)
        if adventure_state["timer"]<=0:
            game_state="gameover"
            if score>high_score:
                high_score=score
                save_high_score(high_score)

    # ------------------ AUTO GAME OVER ------------------
    if game_state in ["playing","adventure"] and not can_place_any_shape():
        game_state = "gameover"
        if score>high_score:
            high_score=score
            save_high_score(high_score)

    # ------------------ RENDER ------------------
    screen.fill(bg_color)

    if game_state=="menu":
        draw_menu(screen, title_font, None, button_font, small_font)
        hs_surf = small_font.render(f"High Score: {high_score}", True, (255,255,255))
        screen.blit(hs_surf, (WIDTH - hs_surf.get_width() - 12, HEIGHT - hs_surf.get_height() - 12))

    elif game_state=="adventure_menu":
        screen.fill((30,30,30))
        adventure_menu.draw(screen)
        draw_back_button(screen)

    else:
        cell_bg = tuple(max(0,min(255,c-40)) for c in bg_color)
        outline_col = (110,90,130)
        grid.draw(screen, cell_bg, outline_col, fallback_block_color)

        screen.blit(title_font.render(f"{score}", True, (255,255,255)), (WIDTH//2 - title_font.size(str(score))[0]//2, 12))
        hs = small_font.render(f"Best: {high_score}", True, (255,255,255))
        screen.blit(hs, (WIDTH - hs.get_width() - 16, 20))

        draw_upcoming_panel(screen)

        if dragging and selected_shape:
            draw_snapped_preview(screen, selected_shape, selected_color, mx, my)

        draw_back_button(screen)

        # adventure HUD
        if game_state=="adventure" and adventure_state:
            name = adventure_state.get("name", f"Level {current_level+1}")
            mode = adventure_state.get("mode")
            screen.blit(small_font.render(f"{name} (Lvl {current_level+1})", True, (255,255,255)), (16,60))
            if mode=="timer":
                timer = int(adventure_state.get("timer",0))
                screen.blit(small_font.render(f"Time: {timer}s", True, (255,255,255)), (16,88))
                screen.blit(small_font.render(f"Target: {adventure_state.get('target',0)}", True, (255,255,255)), (16,108))
            elif mode=="score":
                target = adventure_state.get("target",0)
                screen.blit(small_font.render(f"Target: {target}", True, (255,255,255)), (16,88))

    if game_state=="gameover":
        back_rect, restart_rect = draw_game_over(screen, score, high_score)
        if pygame.mouse.get_pressed()[0]:
            if back_rect.collidepoint(mx,my):
                game_state="menu"
            elif restart_rect.collidepoint(mx,my):
                if adventure_state:
                    start_adventure_level(current_level)
                    game_state="adventure"
                else:
                    reset_game_state()
                    game_state="playing"

    pygame.display.flip()
