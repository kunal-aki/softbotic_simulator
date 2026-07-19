import math
from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self, width=1100, height=750):
        self.sim_width = 3000
        self.sim_height = 2000
        self.sim_depth = 1000.0
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        self.obstacles = []
        self.gravity = [0.0, 500.0, 0.0]
        self.is_3d = False
        self.next_particle_id = 0

        self.grid_cell_size = 50.0
        self.grid = {}

    def add_particle(self, x, y, z=0.0, mass=1.0):
        p = Particle(x, y, z, mass)
        p.body_id = -1
        p.id = self.next_particle_id
        self.next_particle_id += 1
        self.particles.append(p)
        return p

    def add_spring(self, p1, p2, k=500.0, damping=5.0):
        s = Spring(p1, p2, k, damping)
        self.springs.append(s)
        return s

    def remove_particle(self, particle):
        if particle in self.particles: 
            self.particles.remove(particle)
        self.springs = [s for s in self.springs if s.p1 != particle and s.p2 != particle]

    def remove_obstacle(self, obs):
        if obs in self.obstacles: 
            self.obstacles.remove(obs)

    def update_spatial_grid(self):
        self.grid.clear()
        for p in self.particles:
            gx = int(p.pos[0] / self.grid_cell_size)
            gy = int(p.pos[1] / self.grid_cell_size)
            gz = int(p.pos[2] / self.grid_cell_size) if self.is_3d else 0
            key = (gx, gy, gz)
            if key not in self.grid:
                self.grid[key] = []
            self.grid[key].append(p)

    def step(self, dt, substeps=6):
        clamped_dt = min(dt, 0.016)
        sdt = clamped_dt / substeps

        for _ in range(substeps):
            for p in self.particles:
                if not getattr(p, 'is_grabbed', False):
                    p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass, self.gravity[2] * p.mass))

            for s in self.springs: 
                s.update()

            for p in self.particles: 
                p.update(sdt)

            for obs in self.obstacles:
                for p in self.particles:
                    obs.resolve_collision(p, self.is_3d)

            self.resolve_constraints()

            self.update_spatial_grid()
            self.resolve_grid_collisions()

            for sb in self.soft_bodies:
                sb.apply_internal_pressure()
                sb.maintain_volume()

    def resolve_constraints(self):
        floor, ceiling = self.sim_height - 100, 100
        right_wall, left_wall = self.sim_width - 100, 100
        front_wall, back_wall = self.sim_depth, -self.sim_depth

        for p in self.particles:
            if not self.is_3d:
                p.pos[2] = 0.0
                p.prev_pos[2] = 0.0

            if p.pos[1] > floor:
                p.pos[1] = floor
                p.prev_pos[1] = floor + (p.pos[1] - p.prev_pos[1]) * 0.1
            elif p.pos[1] < ceiling:
                p.pos[1] = ceiling
                p.prev_pos[1] = ceiling + (p.pos[1] - p.prev_pos[1]) * 0.1

            if p.pos[0] > right_wall:
                p.pos[0] = right_wall
                p.prev_pos[0] = right_wall + (p.pos[0] - p.prev_pos[0]) * 0.1
            elif p.pos[0] < left_wall:
                p.pos[0] = left_wall
                p.prev_pos[0] = left_wall + (p.pos[0] - p.prev_pos[0]) * 0.1

            if self.is_3d:
                if p.pos[2] > front_wall:
                    p.pos[2] = front_wall
                    p.prev_pos[2] = front_wall + (p.pos[2] - p.prev_pos[2]) * 0.1
                elif p.pos[2] < back_wall:
                    p.pos[2] = back_wall
                    p.prev_pos[2] = back_wall + (p.pos[2] - p.prev_pos[2]) * 0.1

    def resolve_grid_collisions(self):
        # Increased separation radius to prevent overlap locking
        collision_radius = 28.0 if self.is_3d else 24.0
        min_dist_sq = collision_radius * collision_radius
        processed_pairs = set()

        for cell_key, cell_particles in self.grid.items():
            gx, gy, gz = cell_key
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in ([-1, 0, 1] if self.is_3d else [0]):
                        neighbor_key = (gx + dx, gy + dy, gz + dz)
                        if neighbor_key not in self.grid: 
                            continue

                        for p1 in cell_particles:
                            for p2 in self.grid[neighbor_key]:
                                if p1.body_id == p2.body_id or p1.body_id == -1 or p2.body_id == -1: 
                                    continue

                                pair_id = (min(p1.id, p2.id), max(p1.id, p2.id))
                                if pair_id in processed_pairs: 
                                    continue
                                processed_pairs.add(pair_id)

                                x_dist = p2.pos[0] - p1.pos[0]
                                y_dist = p2.pos[1] - p1.pos[1]
                                z_dist = (p2.pos[2] - p1.pos[2]) if self.is_3d else 0.0
                                dist_sq = x_dist * x_dist + y_dist * y_dist + z_dist * z_dist

                                if dist_sq < min_dist_sq:
                                    dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0001
                                    nx, ny, nz = x_dist / dist, y_dist / dist, z_dist / dist

                                    # Full separation displacement prevents bodies from ever sticking together
                                    overlap = (collision_radius - dist) * 0.5
                                    
                                    p1_grabbed = getattr(p1, 'is_grabbed', False)
                                    p2_grabbed = getattr(p2, 'is_grabbed', False)

                                    if not p1.is_static and not p1_grabbed:
                                        p1.pos[0] -= nx * overlap
                                        p1.pos[1] -= ny * overlap
                                        p1.prev_pos[0] -= nx * overlap * 0.5
                                        p1.prev_pos[1] -= ny * overlap * 0.5
                                        if self.is_3d:
                                            p1.pos[2] -= nz * overlap
                                            p1.prev_pos[2] -= nz * overlap * 0.5

                                    if not p2.is_static and not p2_grabbed:
                                        p2.pos[0] += nx * overlap
                                        p2.pos[1] += ny * overlap
                                        p2.prev_pos[0] += nx * overlap * 0.5
                                        p2.prev_pos[1] += ny * overlap * 0.5
                                        if self.is_3d:
                                            p2.pos[2] += nz * overlap
                                            p2.prev_pos[2] += nz * overlap * 0.5


