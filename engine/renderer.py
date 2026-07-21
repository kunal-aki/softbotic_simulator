import pygame


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
        """Safely unpack line points into explicit tuple pairs."""
        try:
            p1 = (int(start_pos[0]), int(start_pos[1]))
            p2 = (int(end_pos[0]), int(end_pos[1]))
            pygame.draw.line(self.surface, color, p1, p2, int(width))
        except (TypeError, IndexError):
            pass

    def draw_circle(self, color, center_pos, radius, width=0):
        """Safely unpack circle center coordinates."""
        try:
            center = (int(center_pos[0]), int(center_pos[1]))
            r = max(1, int(radius))
            pygame.draw.circle(self.surface, color, center, r, int(width))
        except (TypeError, IndexError):
            pass

    def draw_rect(self, color, rect, width=0, border_radius=0):
        """Safely format rectangle parameters."""
        try:
            if isinstance(rect, (list, tuple)):
                r = pygame.Rect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            else:
                r = rect
            pygame.draw.rect(self.surface, color, r, int(width), border_radius=int(border_radius))
        except (TypeError, IndexError):
            pass

    def draw_viewport_border(self, viewport_rect, color=(85, 85, 95), width=1):
        """Draw viewport border outline."""
        pygame.draw.rect(self.surface, color, viewport_rect, width)

    def draw_selection(self, selected_obj, camera):
        """Highlight selected object."""
        if not selected_obj:
            return

        cam_x = getattr(camera, 'x', getattr(camera, 'offset_x', 0.0))
        cam_y = getattr(camera, 'y', getattr(camera, 'offset_y', 0.0))
        zoom = getattr(camera, 'zoom', 1.0)

        if isinstance(selected_obj, dict):
            wx = float(selected_obj.get('x', 0.0))
            wy = float(selected_obj.get('y', 0.0))
            sx = int((wx + cam_x) * zoom)
            sy = int((wy + cam_y) * zoom)

            self.draw_circle((255, 200, 50), (sx, sy), int(22 * zoom), width=2)


