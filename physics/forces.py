import math

class Spring:
    def __init__(self, p1, p2, k=150.0, damping=1.5):
        self.p1 = p1
        self.p2 = p2
        self.k = k
        self.damping = damping
        
        dx = self.p2.pos[0] - self.p1.pos[0]
        dy = self.p2.pos[1] - self.p1.pos[1]
        self.rest_length = math.sqrt(dx*dx + dy*dy)
        if self.rest_length == 0:
            self.rest_length = 1.0

        self.color = (150, 150, 160)

    def update(self, dt):
        dx = self.p2.pos[0] - self.p1.pos[0]
        dy = self.p2.pos[1] - self.p1.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist

        # Hooke's Structural Restoring Force
        displacement = dist - self.rest_length
        spring_force_mag = displacement * self.k

        # Axial Damping projection
        v1x = self.p1.pos[0] - self.p1.prev_pos[0]
        v1y = self.p1.pos[1] - self.p1.prev_pos[1]
        v2x = self.p2.pos[0] - self.p2.prev_pos[0]
        v2y = self.p2.pos[1] - self.p2.prev_pos[1]
        
        rvx = v2x - v1x
        rvy = v2y - v1y
        damping_force_mag = (rvx * nx + rvy * ny) * self.damping

        total_force = spring_force_mag + damping_force_mag

        self.p1.apply_force((nx * total_force, ny * total_force))
        self.p2.apply_force((-nx * total_force, -ny * total_force))

    def draw(self, renderer, camera):
        p1_screen = camera.world_to_screen(self.p1.pos)
        p2_screen = camera.world_to_screen(self.p2.pos)
        width = max(1, int(2 * camera.zoom))
        renderer.draw_line(self.color, p1_screen, p2_screen, width)


