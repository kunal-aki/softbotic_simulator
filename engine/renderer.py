"""
BioSim v2.0 - Viewport & Graphics Renderer
Provides high-level drawing, clipping, grid rendering, and coordinate axes.
"""

import pygame
from engine.config import (
    VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
    COLOR_GRID, COLOR_AXIS_X, COLOR_AXIS_Y, COLOR_SELECTION, COLOR_BORDER, GRID_SIZE
)


class Renderer:
    def __init__(self, surface):
        self.surface = surface

    def clear(self, color):
        self.surface.fill(color)

    def set_clip(self, rect):
        self.surface.set_clip(rect)

    def clear_clip(self):
        self.surface.set_clip(None)

    def draw_line(self, color, start_pos, end_pos, width=1):
        try:
            p1 = (int(start_pos[0]), int(start_pos[1]))
            p2 = (int(end_pos[0]), int(end_pos[1]))
            pygame.draw.line(self.surface, color, p1, p2, int(width))
        except (TypeError, ValueError):
            pass

    def draw_circle(self, color, center_pos, radius, width=0):
        try:
            center = (int(center_pos[0]), int(center_pos[1]))
            r = max(1, int(radius))
            pygame.draw.circle(self.surface, color, center, r, int(width))
        except (TypeError, ValueError):
            pass

    def draw_rect(self, color, rect, width=0, border_radius=0):
        try:
            r = pygame.Rect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            pygame.draw.rect(self.surface, color, r, int(width), border_radius=int(border_radius))
        except (TypeError, ValueError):
            pass

    def draw_grid_and_axes(self, camera):
        viewport = pygame.Rect(VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        spacing = GRID_SIZE * camera.zoom

        if spacing >= 6:
            ox = (camera.x * camera.zoom) % spacing
            oy = (camera.y * camera.zoom) % spacing

            x = viewport.left - spacing
            while x < viewport.right + spacing:
                sx = int(x + ox)
                if viewport.left <= sx <= viewport.right:
                    pygame.draw.line(self.surface, COLOR_GRID, (sx, viewport.top), (sx, viewport.bottom), 1)
                x += spacing

            y = viewport.top - spacing
            while y < viewport.bottom + spacing:
                sy = int(y + oy)
                if viewport.top <= sy <= viewport.bottom:
                    pygame.draw.line(self.surface, COLOR_GRID, (viewport.left, sy), (viewport.right, sy), 1)
                y += spacing

        # Draw World Coordinate Origin Axes
        origin_sx = int((0.0 + camera.x) * camera.zoom) + VIEWPORT_X
        origin_sy = int((0.0 + camera.y) * camera.zoom) + VIEWPORT_Y

        if viewport.top <= origin_sy <= viewport.bottom:
            pygame.draw.line(self.surface, COLOR_AXIS_X, (viewport.left, origin_sy), (viewport.right, origin_sy), 2)
        if viewport.left <= origin_sx <= viewport.right:
            pygame.draw.line(self.surface, COLOR_AXIS_Y, (origin_sx, viewport.top), (origin_sx, viewport.bottom), 2)

    def draw_selection_gizmo(self, obj, camera):
        if not obj or not getattr(obj, "visible", True):
            return

        aabb = obj.get_aabb()
        if not aabb:
            return

        min_x, min_y, max_x, max_y = aabb

        sx1 = int((min_x + camera.x) * camera.zoom) + VIEWPORT_X - 6
        sy1 = int((min_y + camera.y) * camera.zoom) + VIEWPORT_Y - 6
        sx2 = int((max_x + camera.x) * camera.zoom) + VIEWPORT_X + 6
        sy2 = int((max_y + camera.y) * camera.zoom) + VIEWPORT_Y + 6

        w = max(12, sx2 - sx1)
        h = max(12, sy2 - sy1)

        # Highlight Bounding Box
        pygame.draw.rect(self.surface, COLOR_SELECTION, (sx1, sy1, w, h), 1)

        # Corner Handles
        handle_size = 6
        for hx, hy in [(sx1, sy1), (sx1 + w, sy1), (sx1, sy1 + h), (sx1 + w, sy1 + h)]:
            pygame.draw.rect(self.surface, COLOR_SELECTION, (hx - handle_size // 2, hy - handle_size // 2, handle_size, handle_size))

    def draw_viewport_border(self):
        viewport = pygame.Rect(VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        pygame.draw.rect(self.surface, COLOR_BORDER, viewport, 1)


