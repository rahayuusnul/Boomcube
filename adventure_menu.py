# adventure_menu.py
import pygame

pygame.font.init()
small_font = pygame.font.SysFont("Arial", 16, bold=True)

class AdventureMenu:
    def __init__(self, total_levels=50, cols=10, spacing=60, screen_width=480, screen_height=800, y_offset=150):
        self.total_levels = total_levels
        self.cols = cols
        self.spacing = spacing
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.y_offset = y_offset  # offset vertikal agar level agak ke bawah

        self.levels = [True] + [False]*(total_levels-1)  # unlock status
        self.scroll_x = 0
        self.scroll_y = 0

        # load lock icon
        try:
            self.lock_img = pygame.image.load("assets/lock.png").convert_alpha()
        except:
            self.lock_img = None
        # load out icon
        try:
            self.out_img = pygame.image.load("assets/out.png").convert_alpha()
        except:
            self.out_img = None

    def get_node_pos(self, idx):
        row = idx // self.cols
        col = idx % self.cols
        # zig-zag path
        if row % 2 == 1:
            col = self.cols - 1 - col
        x = col * self.spacing - self.scroll_x + self.spacing//2
        y = row * self.spacing - self.scroll_y + self.spacing//2 + self.y_offset
        return x, y

    def draw(self, surf):
        surf.fill((30,30,30))
        for idx in range(self.total_levels):
            x, y = self.get_node_pos(idx)
            if x < -50 or x > self.screen_width+50 or y < -50 or y > self.screen_height+50:
                continue

            unlocked = self.levels[idx]
            radius = 20
            color = (100,200,100) if unlocked else (180,180,180)
            pygame.draw.circle(surf, color, (x,y), radius)
            pygame.draw.circle(surf, (0,0,0), (x,y), radius, 2)

            # Tampilkan nomor level
            num_surf = small_font.render(str(idx+1), True, (0,0,0))
            surf.blit(num_surf, (x - num_surf.get_width()//2, y - num_surf.get_height()//2))

            # Lock icon untuk level terkunci
            if not unlocked:
                if self.lock_img:
                    lock_size = 24
                    lock_surf = pygame.transform.smoothscale(self.lock_img, (lock_size, lock_size))
                    surf.blit(lock_surf, (x-lock_size//2, y-lock_size//2))
                else:
                    lock_size = 16
                    lock_rect = pygame.Rect(x-lock_size//2, y-lock_size//2, lock_size, lock_size)
                    pygame.draw.rect(surf, (80,80,80), lock_rect, border_radius=4)
                    pygame.draw.line(surf, (50,50,50), (lock_rect.x, lock_rect.y+lock_size//2),
                                     (lock_rect.x+lock_size, lock_rect.y+lock_size//2), 2)
                    pygame.draw.arc(surf, (50,50,50), (lock_rect.x, lock_rect.y-4, lock_size, lock_size), 3.14, 0, 2)

    def click(self, pos):
        """Return 1-based level index if unlocked, False if locked, None if nothing"""
        for idx in range(self.total_levels):
            x, y = self.get_node_pos(idx)
            r = 20
            dx, dy = pos[0]-x, pos[1]-y
            if dx*dx + dy*dy <= r*r:
                if self.levels[idx]:
                    return idx+1
                else:
                    return False
        return None

    def unlock_next_level(self, idx):
        if idx+1 < len(self.levels):
            self.levels[idx+1] = True

    def scroll(self, dx, dy):
        rows = (self.total_levels + self.cols - 1) // self.cols
        max_x = max(0, self.cols*self.spacing - self.screen_width)
        max_y = max(0, rows*self.spacing - self.screen_height + self.y_offset)
        self.scroll_x = min(max(self.scroll_x + dx, 0), max_x)
        self.scroll_y = min(max(self.scroll_y + dy, 0), max_y)
