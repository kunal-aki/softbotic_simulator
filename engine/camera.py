"""
BioSim v2.0 - CAD Camera System
Handles 2D viewport pan and zoom transformations.
"""

class Camera:
    def __init__(self, x=0.0, y=0.0, zoom=1.0):
        self.x = float(x)
        self.y = float(y)
        self.zoom = float(zoom)
        self.min_zoom = 0.15
        self.max_zoom = 8.0

    def move(self, dx, dy):
        self.x += dx / self.zoom
        self.y += dy / self.zoom

    def zoom_at(self, factor, focus_screen_x, focus_screen_y, viewport_x, viewport_y):
        old_zoom = self.zoom
        new_zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        if old_zoom == new_zoom:
            return

        # Zoom towards cursor
        rel_x = focus_screen_x - viewport_x
        rel_y = focus_screen_y - viewport_y

        world_before_x = (rel_x / old_zoom) - self.x
        world_before_y = (rel_y / old_zoom) - self.y

        self.zoom = new_zoom

        self.x = (rel_x / self.zoom) - world_before_x
        self.y = (rel_y / self.zoom) - world_before_y


