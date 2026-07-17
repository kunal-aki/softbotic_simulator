import os
import sys

# Ensure root directory is searchable for packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self):
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        self.obstacles = []
        
        self.gravity = [0.0, 980.0]  # Standard downward acceleration
        self.floor_y = 600.0         # Ground level bound boundary

    def add_particle(self, x, y, mass=1.0, is_static=False):
        """Spawns a new particle into the simulator environment."""
        p = Particle(x, y, mass, is_static)
        self.particles.append(p)
        return p

    def add_spring(self, p1, p2, k=150.0, damping=1.5):
        """Creates an elastic structural spring link between two particles."""
        s = Spring(p1, p2, k, damping)
        self.springs.append(s)
        return s

    def remove_particle(self, particle):
        """Cleanly removes a particle and slices away any connecting springs."""
        if particle in self.particles:
            self.particles.remove(particle)
        # Keeps only the springs that aren't attached to the deleted node
        self.springs = [s for s in self.springs if s.p1 != particle and s.p2 != particle]

    def update(self, dt):
        # 🎯 Dynamic Pressure Check: Forces soft bodies to retain volume
        if hasattr(self, 'soft_bodies'):
            for sb in self.soft_bodies:
                sb.apply_pressure()

        for p in self.particles:
            p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass))

        for s in self.springs:
            s.update(dt)

        for p in self.particles:
            p.update(dt)

        # Environment Bounds Detection
        for p in self.particles:
            if p.pos[1] > self.floor_y - p.radius:
                p.pos[1] = self.floor_y - p.radius
                prev_vel_x = p.pos[0] - p.prev_pos[0]
                p.prev_pos[0] = p.pos[0] - prev_vel_x * 0.95
                p.prev_pos[1] = p.pos[1]

    def draw(self, renderer, camera):
        """Renders the horizontal floor boundary and all active entities."""
        floor_start = camera.world_to_screen((-5000, self.floor_y))
        floor_end = camera.world_to_screen((5000, self.floor_y))
        renderer.draw_line((200, 100, 100), floor_start, floor_end, 2)

        for s in self.springs:
            s.draw(renderer, camera)

        for p in self.particles:
            p.draw(renderer, camera)


