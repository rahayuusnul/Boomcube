# achievement_menu.py

import pygame

# Dummy data for demonstration; in a real game, replace with actual player data
STATISTICS = {
    "Highest Combo": "95",
    "Best Score": "338586",
    "Rounds": "653",
    "Login Days": "41"
}

ACHIEVEMENTS = [
    {"name": "Invincible", "unlocked": True},
    {"name": "Perseverance", "unlocked": True},
    {"name": "Jewelry Tycoon", "unlocked": False},
    {"name": "Score Champion", "unlocked": True},
    {"name": "Block Master", "unlocked": False},
    {"name": "Opportunist", "unlocked": True},
    {"name": "Unwavering", "unlocked": False},
    {"name": "Master Cleaner", "unlocked": True},
    {"name": "Adventurer", "unlocked": False},
]

class AchievementMenu:
    def __init__(self):
        # Fonts
        self.font_title = pygame.font.Font(None, 70)
        self.font_stat = pygame.font.Font(None, 50)
        self.font_text = pygame.font.Font(None, 36)
        self.font_award = pygame.font.Font(None, 28)

        # Layout
        self.margin_x = 40
        self.margin_y = 40
        self.stat_box_height = 80
        self.stat_gap = 20
        self.award_gap = 16
        self.award_cols = 3  # number of awards per row

    def draw(self, screen):
        screen.fill((40, 60, 120))

        # Title
        title_surf = self.font_title.render("Achievements", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width()//2 - title_surf.get_width()//2, 20))

        # Draw Statistics
        y = 120
        for label, value in STATISTICS.items():
            box_rect = pygame.Rect(self.margin_x, y, screen.get_width() - 2*self.margin_x, self.stat_box_height)
            pygame.draw.rect(screen, (80, 100, 160), box_rect, border_radius=12)

            val_surf = self.font_stat.render(str(value), True, (255, 200, 0))
            lbl_surf = self.font_stat.render(label, True, (230, 230, 230))

            screen.blit(val_surf, (box_rect.x + 20, box_rect.y + 20))
            screen.blit(lbl_surf, (box_rect.x + 220, box_rect.y + 22))
            y += self.stat_box_height + self.stat_gap

        # Draw Awards
        y += 20  # space after statistics
        award_box_size = 90
        start_x = self.margin_x
        for idx, award in enumerate(ACHIEVEMENTS):
            col = idx % self.award_cols
            row = idx // self.award_cols
            x = start_x + col * (award_box_size + self.award_gap)
            ay = y + row * (award_box_size + 50)

            box_rect = pygame.Rect(x, ay, award_box_size, award_box_size)
            color = (255, 215, 0) if award["unlocked"] else (100, 100, 100)
            pygame.draw.rect(screen, color, box_rect, border_radius=12)
            pygame.draw.rect(screen, (50,50,50), box_rect, 3, border_radius=12)

            # Award name
            text_surf = self.font_award.render(award["name"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(box_rect.centerx, box_rect.bottom + 16))
            screen.blit(text_surf, text_rect)

        # Back Button
        self.back_rect = pygame.Rect(20, 20, 60, 50)
        pygame.draw.rect(screen, (255, 255, 255), self.back_rect, border_radius=10)
        back_surf = self.font_text.render("<", True, (0, 0, 0))
        screen.blit(back_surf, (self.back_rect.centerx - back_surf.get_width()//2,
                                self.back_rect.centery - back_surf.get_height()//2))

    def click(self, pos):
        if self.back_rect.collidepoint(pos):
            return "back"
        return None
