import pygame

class Particle:
    def __init__(self, x, y, mass=1.0, is_static=False):
        self.pos = [float(x), float(y)]
        self.prev_pos = [float(x), float(y)]
        self.acc = [0.0, 0.0]
        
        self.mass = mass
        self.is_static = is_static
        self.radius = 6.0
        self.color = (50, 200, 100) if not is_static else (200, 80, 80)

    def apply_force(self, force):
        if self.is_static:
            return
        self.acc[0] += force[0] / self.mass
        self.acc[1] += force[1] / self.mass

    def update(self, dt):
        if self.is_static:
            return

        temp_x = self.pos[0]
        temp_y = self.pos[1]

        # Explicit implicit velocity + structural damping (air resistance)
        vel_x = (self.pos[0] - self.prev_pos[0]) * 0.99
        vel_y = (self.pos[1] - self.prev_pos[1]) * 0.99

        # Position shift step
        self.pos[0] += vel_x + self.acc[0] * dt * dt
        self.pos[1] += vel_y + self.acc[1] * dt * dt

        self.prev_pos[0] = temp_x
        self.prev_pos[1] = temp_y

        self.acc = [0.0, 0.0]

    def draw(self, renderer, camera):
        screen_pos = camera.world_to_screen(self.pos)
        scaled_radius = max(2, int(self.radius * camera.zoom))
        renderer.draw_circle(self.color, screen_pos, scaled_radius)


