import os
import sys
# Back up one level to include root in engine files just in case
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self):
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        self.obstacles = []
        
        self.gravity = [0.0, 980.0]  # Gravity constant in world coordinate pixels/s^2
        self.floor_y = 700.0         # Spatial environment boundary floor line

    def add_particle(self, x, y, mass=1.0, is_static=False):
        p = Particle(x, y, mass, is_static)
        self.particles.append(p)
        return p

    def add_spring(self, p1, p2, k=150.0, damping=1.5):
        s = Spring(p1, p2, k, damping)
        self.springs.append(s)
        return s

    def update(self, dt):
        # 1. Distribute global environment forces
        for p in self.particles:
            p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass))

        # 2. Process spring constraint shifts
        for s in self.springs:
            s.update(dt)

        # 3. Integrate state math equations
        for p in self.particles:
            p.update(dt)

        # 4. Enforce floor collisions
        for p in self.particles:
            if p.pos[1] > self.floor_y - p.radius:
                p.pos[1] = self.floor_y - p.radius
                # Structural ground friction & inelastic collapse properties
                prev_vel_x = p.pos[0] - p.prev_pos[0]
                p.prev_pos[0] = p.pos[0] - prev_vel_x * 0.95
                p.prev_pos[1] = p.pos[1]

    def draw(self, renderer, camera):
        # Render engineering boundary environment line
        floor_start = camera.world_to_screen((-5000, self.floor_y))
        floor_end = camera.world_to_screen((5000, self.floor_y))
        renderer.draw_line((200, 100, 100), floor_start, floor_end, 2)

        # Render spring structures first
        for s in self.springs:
            s.draw(renderer, camera)

        # Overlay physics nodes
        for p in self.particles:
            p.draw(renderer, camera)


