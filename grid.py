#grid.py

GRID_SIZE = 8
CELL_SIZE = 56
EMPTY = -1

class Grid:
    def __init__(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.size = GRID_SIZE
        self.EMPTY = EMPTY
        self.cells = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def draw(self, surf, cell_bg, outline_color, block_color):
        import pygame
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rx = self.offset_x + x * CELL_SIZE
                ry = self.offset_y + y * CELL_SIZE
                rect = pygame.Rect(rx, ry, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surf, cell_bg, rect, border_radius=8)
                inner = rect.inflate(-8, -8)
                pygame.draw.rect(surf, (255,255,255), inner, border_radius=6)
                pygame.draw.rect(surf, outline_color, inner, 2, border_radius=6)
                if self.cells[y][x] != EMPTY:
                    block_color_real = self.cells[y][x]
                    block = inner.inflate(-6, -6)
                    pygame.draw.rect(surf, block_color_real, block, border_radius=6)
                    pygame.draw.rect(surf, outline_color, block, 2, border_radius=6)

    def can_place(self, shape, gx, gy):
        for sx, sy in shape:
            nx = gx + sx
            ny = gy + sy
            if nx < 0 or ny < 0 or nx >= GRID_SIZE or ny >= GRID_SIZE:
                return False
            if self.cells[ny][nx] != EMPTY:
                return False
        return True

    def place(self, shape, gx, gy, color_value):
        for sx, sy in shape:
            self.cells[gy + sy][gx + sx] = color_value

    def clear_full_lines(self):
        cleared = 0
        cleared_cells = []

        rows = [y for y in range(GRID_SIZE) if all(self.cells[y][x] != EMPTY for x in range(GRID_SIZE))]
        for y in rows:
            for x in range(GRID_SIZE):
                self.cells[y][x] = EMPTY
                cleared_cells.append((x,y))
            cleared += 1

        cols = [x for x in range(GRID_SIZE) if all(self.cells[y][x] != EMPTY for y in range(GRID_SIZE))]
        for x in cols:
            for y in range(GRID_SIZE):
                self.cells[y][x] = EMPTY
                cleared_cells.append((x,y))
            cleared += 1

        return cleared, cleared_cells

    def clear_all(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.cells[y][x] = EMPTY

    def contains_shape(self, shape):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.can_place(shape, x, y):
                    return True
        return False
