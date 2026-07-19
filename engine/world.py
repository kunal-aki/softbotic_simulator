import math
from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self, width=1000, height=700):
        self.width = width
        self.height = height
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        # Updated to full 3D acceleration vectors
        self.gravity = [0.0, 450.0, 0.0] 

    def add_particle(self, x, y, z=0.0, mass=1.0):
        p = Particle(x, y, z, mass)
        self.particles.append(p)
        return p

    def add_spring(self, p1, p2, k=500.0, damping=5.0):
        s = Spring(p1, p2, k, damping)
        self.springs.append(s)
        return s

    def step(self, dt, substeps=4):
        sdt = dt / substeps
        for _ in range(substeps):
            for p in self.particles:
                p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass, self.gravity[2] * p.mass))
            
            for s in self.springs:
                s.update()
                
            for p in self.particles:
                p.update(sdt)
                
            self.resolve_constraints()
            self.resolve_soft_body_collisions()

    def resolve_constraints(self):
        # Boundaries adjusted for spatial cube volume restrictions
        floor, ceiling = self.height - 40, 40
        right_wall, left_wall = self.width - 40, 40
        front_wall, back_wall = 250.0, -250.0
        bounce_damp = 0.4

        for p in self.particles:
            # Y Axis Collision Floor/Ceiling
            if p.pos[1] > floor:
                p.pos[1] = floor
                p.prev_pos[1] = floor + (p.pos[1] - p.prev_pos[1]) * bounce_damp
            elif p.pos[1] < ceiling:
                p.pos[1] = ceiling
                p.prev_pos[1] = ceiling + (p.pos[1] - p.prev_pos[1]) * bounce_damp

            # X Axis Collision Walls
            if p.pos[0] > right_wall:
                p.pos[0] = right_wall
                p.prev_pos[0] = right_wall + (p.pos[0] - p.prev_pos[0]) * bounce_damp
            elif p.pos[0] < left_wall:
                p.pos[0] = left_wall
                p.prev_pos[0] = left_wall + (p.pos[0] - p.prev_pos[0]) * bounce_damp

            # Z Axis Depth Boundaries
            if p.pos[2] > front_wall:
                p.pos[2] = front_wall
                p.prev_pos[2] = front_wall + (p.pos[2] - p.prev_pos[2]) * bounce_damp
            elif p.pos[2] < back_wall:
                p.pos[2] = back_wall
                p.prev_pos[2] = back_wall + (p.pos[2] - p.prev_pos[2]) * bounce_damp

    def resolve_soft_body_collisions(self):
        num_bodies = len(self.soft_bodies)
        if num_bodies < 2: return

        repulsion_radius = 45.0
        repulsion_stiffness = 1400.0
        repulsion_damping = 8.0

        for i in range(num_bodies):
            for j in range(i + 1, num_bodies):
                b1 = self.soft_bodies[i]
                b2 = self.soft_bodies[j]

                for p1 in b1.particles:
                    for p2 in b2.particles:
                        dx = p2.pos[0] - p1.pos[0]
                        dy = p2.pos[1] - p1.pos[1]
                        dz = p2.pos[2] - p1.pos[2]
                        dist_sq = dx*dx + dy*dy + dz*dz

                        if dist_sq < (repulsion_radius * repulsion_radius) and dist_sq > 0.001:
                            dist = math.sqrt(dist_sq)
                            nx, ny, nz = dx / dist, dy / dist, dz / dist
                            penetration = repulsion_radius - dist

                            v1x = p1.pos[0] - p1.prev_pos[0]
                            v1y = p1.pos[1] - p1.prev_pos[1]
                            v1z = p1.pos[2] - p1.prev_pos[2]
                            v2x = p2.pos[0] - p2.prev_pos[0]
                            v2y = p2.pos[1] - p2.prev_pos[1]
                            v2z = p2.pos[2] - p2.prev_pos[2]

                            rvx = v2x - v1x
                            rvy = v2y - v1y
                            rvz = v2z - v1z

                            push = penetration * repulsion_stiffness
                            damp = (rvx * nx + rvy * ny + rvz * nz) * repulsion_damping
                            total_force = max(0.0, push - damp)

                            fx, fy, fz = nx * total_force, ny * total_force, nz * total_force
                            if not p1.is_static: p1.apply_force((-fx, -fy, -fz))
                            if not p2.is_static: p2.apply_force((fx, fy, fz))


