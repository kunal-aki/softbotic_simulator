import pygame


class Scene:

    def __init__(self):
        self.objects = []

    def update(self, dt):
        """Update physics/state for all scene objects safely."""
        # Ensure dt is passed as float
        dt_val = float(dt)

        for obj in list(self.objects):
            # Skip invalid primitive entries (like accidental floats or non-objects)
            if not isinstance(obj, (dict, object)) or isinstance(obj, (float, int, str)):
                continue

            if hasattr(obj, 'update') and callable(getattr(obj, 'update')):
                try:
                    obj.update(dt_val)
                except TypeError as e:
                    # Catch cases where an internal physics object expects sub-step iterables or tuples
                    try:
                        obj.update([dt_val])
                    except Exception:
                        pass

    def draw(self, renderer, camera):
        """Render scene objects through the camera viewport."""
        cam_x = float(getattr(camera, 'x', getattr(camera, 'offset_x', 0.0)))
        cam_y = float(getattr(camera, 'y', getattr(camera, 'offset_y', 0.0)))
        zoom = float(getattr(camera, 'zoom', 1.0))

        for obj in self.objects:
            if hasattr(obj, 'draw') and callable(getattr(obj, 'draw')):
                obj.draw(renderer, camera)

            elif isinstance(obj, dict):
                wx = float(obj.get('x', 0.0))
                wy = float(obj.get('y', 0.0))

                screen_x = int((wx + cam_x) * zoom)
                screen_y = int((wy + cam_y) * zoom)
                screen_pos = (screen_x, screen_y)

                obj_type = obj.get('type', 'particle')

                if obj_type == 'particle':
                    renderer.draw_circle((100, 200, 255), screen_pos, int(6 * zoom))
                elif obj_type in ['square', 'rect', 'Rect']:
                    size = int(30 * zoom)
                    rect = (
                        screen_x - size // 2,
                        screen_y - size // 2,
                        size,
                        size
                    )
                    renderer.draw_rect((220, 120, 80), rect)
                elif obj_type in ['circle', 'Circle']:
                    renderer.draw_circle((120, 220, 120), screen_pos, int(18 * zoom))

    def render(self, renderer, camera):
        self.draw(renderer, camera)

    def pick_object(self, world_pos):
        wx, wy = world_pos
        for obj in reversed(self.objects):
            if hasattr(obj, 'contains_point') and callable(getattr(obj, 'contains_point')):
                if obj.contains_point(wx, wy):
                    return obj
            elif isinstance(obj, dict) and 'x' in obj and 'y' in obj:
                dx = float(obj['x']) - wx
                dy = float(obj['y']) - wy
                if (dx * dx + dy * dy) < 900:  # 30px click threshold
                    return obj
        return None

    def add_object(self, obj_or_type, x=0.0, y=0.0, **kwargs):
        if isinstance(obj_or_type, str):
            obj = {
                "type": obj_or_type,
                "x": float(kwargs.get("x", x)),
                "y": float(kwargs.get("y", y))
            }
        else:
            obj = obj_or_type

        # Ensure we only append valid object types
        if obj is not None and not isinstance(obj, (float, int)):
            self.objects.append(obj)
        return obj

    def add_particle(self, x, y):
        return self.add_object("particle", x=x, y=y)

    def create_soft_body(self, x, y, shape="square"):
        return self.add_object(shape, x=x, y=y)


