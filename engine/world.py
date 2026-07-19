import math
from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self, width=1100, height=750):
        self.sim_width = 4000
        self.sim_height = 3000
        self.sim_depth = 2000.0
        
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        self.obstacles = []
        self.gravity = [0.0, 500.0, 0.0] 
        self.is_3d = False # Starts explicitly in 2D layout mode
        
        # Unique identification counter for unique pair hashing
        self.next_particle_id = 0
        
        # Spatial Partition Grid Setup
        self.grid_cell_size = 55.0
        self.grid = {}

    def add_particle(self, x, y, z=0.0, mass=1.0):
        p = Particle(x, y, z, mass)
        p.body_id = -1
        
        # Fixed tracking ID attribute assigned directly to the instance node
        p.id = self.next_particle_id
        self.next_particle_id += 1
        
        self.particles.append(p)
        return p

    def add_spring(self, p1, p2, k=500.0, damping=5.0):
        s = Spring(p1, p2, k, damping)
        self.springs.append(s)
        return s

    def remove_particle(self, particle):
        if particle in self.particles: self.particles.remove(particle)
        self.springs = [s for s in self.springs if s.p1 != particle and s.p2 != particle]
        for sb in self.soft_bodies:
            if particle in sb.particles: sb.particles.remove(particle)
            sb.springs = [s for s in sb.springs if s.p1 != particle and s.p2 != particle]
        self.soft_bodies = [sb for sb in self.soft_bodies if len(sb.particles) > 0]

    def remove_obstacle(self, obs):
        if obs in self.obstacles: self.obstacles.remove(obs)

    def update_spatial_grid(self):
        """Hashes particle references into spatial voxel buckets."""
        self.grid.clear()
        for p in self.particles:
            gx = int(p.pos[0] / self.grid_cell_size)
            gy = int(p.pos[1] / self.grid_cell_size)
            gz = int(p.pos[2] / self.grid_cell_size) if self.is_3d else 0
            key = (gx, gy, gz)
            if key not in self.grid:
                self.grid[key] = []
            self.grid[key].append(p)

    def step(self, dt, substeps=4):
        # High performance clamping loop for 120Hz tracking matrices
        clamped_dt = min(dt, 0.01)
        sdt = clamped_dt / substeps
        
        for _ in range(substeps):
            for p in self.particles:
                p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass, self.gravity[2] * p.mass))
            for s in self.springs: s.update()
            for p in self.particles: p.update(sdt)
            for obs in self.obstacles:
                for p in self.particles: obs.resolve_collision(p, self.is_3d)
            self.resolve_constraints()
            
            # Optimized Collision Pass
            self.update_spatial_grid()
            self.resolve_grid_collisions()
            
            for sb in self.soft_bodies: sb.maintain_volume()

    def resolve_constraints(self):
        floor, ceiling = self.sim_height - 100, 100
        right_wall, left_wall = self.sim_width - 100, 100
        front_wall, back_wall = self.sim_depth, -self.sim_depth
        bounce = 0.05

        for p in self.particles:
            if not self.is_3d:
                p.pos[2] = 0.0
                p.prev_pos[2] = 0.0
            if p.pos[1] > floor:
                p.pos[1] = floor
                p.prev_pos[1] = floor + (p.pos[1] - p.prev_pos[1]) * bounce
            elif p.pos[1] < ceiling:
                p.pos[1] = ceiling
                p.prev_pos[1] = ceiling + (p.pos[1] - p.prev_pos[1]) * bounce
            if p.pos[0] > right_wall:
                p.pos[0] = right_wall
                p.prev_pos[0] = right_wall + (p.pos[0] - p.prev_pos[0]) * bounce
            elif p.pos[0] < left_wall:
                p.pos[0] = left_wall
                p.prev_pos[0] = left_wall + (p.pos[0] - p.prev_pos[0]) * bounce
            if self.is_3d:
                if p.pos[2] > front_wall:
                    p.pos[2] = front_wall
                    p.prev_pos[2] = front_wall + (p.pos[2] - p.prev_pos[2]) * bounce
                elif p.pos[2] < back_wall:
                    p.pos[2] = back_wall
                    p.prev_pos[2] = back_wall + (p.pos[2] - p.prev_pos[2]) * bounce

    def resolve_grid_collisions(self):
        """Resolves collisions using nearby grid cells instead of checking all pairs."""
        collision_radius = 46.0 if self.is_3d else 34.0
        min_dist_sq = collision_radius * collision_radius
        bounce, fric, push_factor = 0.10, 0.90, 0.65
        processed_pairs = set()

        for cell_key, cell_particles in self.grid.items():
            gx, gy, gz = cell_key
            # Search adjacent cells (3x3x3 neighborhood space)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1] if self.is_3d else [0]:
                        neighbor_key = (gx + dx, gy + dy, gz + dz)
                        if neighbor_key not in self.grid: continue
                        
                        for p1 in cell_particles:
                            for p2 in self.grid[neighbor_key]:
                                if p1.body_id == p2.body_id or p1.body_id == -1 or p2.body_id == -1: continue
                                pair_id = (min(p1.id, p2.id), max(p1.id, p2.id))
                                if pair_id in processed_pairs: continue
                                processed_pairs.add(pair_id)

                                x_dist = p2.pos[0] - p1.pos[0]
                                y_dist = p2.pos[1] - p1.pos[1]
                                z_dist = p2.pos[2] - p1.pos[2] if self.is_3d else 0.0
                                dist_sq = x_dist*x_dist + y_dist*y_dist + z_dist*z_dist

                                if dist_sq < min_dist_sq:
                                    dist = math.sqrt(dist_sq) if dist_sq > 0.001 else 0.001
                                    
                                    # Safe outward calculation tracking via structural parent centers
                                    sb1 = self.soft_bodies[p1.body_id] if p1.body_id < len(self.soft_bodies) else None
                                    sb2 = self.soft_bodies[p2.body_id] if p2.body_id < len(self.soft_bodies) else None
                                    
                                    if sb1 and sb2:
                                        c1, c2 = sb1.get_center_of_mass(), sb2.get_center_of_mass()
                                        nx, ny, nz = c2[0]-c1[0], c2[1]-c1[1], (c2[2]-c1[2] if self.is_3d else 0.0)
                                        n_len = math.sqrt(nx*nx + ny*ny + nz*nz)
                                        if n_len > 0.001: nx, ny, nz = nx/n_len, ny/n_len, nz/n_len
                                        else: nx, ny, nz = x_dist/dist, y_dist/dist, z_dist/dist
                                    else:
                                        nx, ny, nz = x_dist/dist, y_dist/dist, z_dist/dist

                                    overlap = (collision_radius - dist) * push_factor * 0.5

                                    if not p1.is_static:
                                        p1.pos[0] -= nx * overlap; p1.pos[1] -= ny * overlap
                                        p1.prev_pos[0] -= nx * overlap; p1.prev_pos[1] -= ny * overlap
                                        if self.is_3d: p1.pos[2] -= nz * overlap; p1.prev_pos[2] -= nz * overlap
                                    if not p2.is_static:
                                        p2.pos[0] += nx * overlap; p2.pos[1] += ny * overlap
                                        p2.prev_pos[0] += nx * overlap; p2.prev_pos[1] += ny * overlap
                                        if self.is_3d: p2.pos[2] += nz * overlap; p2.prev_pos[2] += nz * overlap

                                    v1x, v1y, v1z = p1.pos[0]-p1.prev_pos[0], p1.pos[1]-p1.prev_pos[1], p1.pos[2]-p1.prev_pos[2]
                                    v2x, v2y, v2z = p2.pos[0]-p2.prev_pos[0], p2.pos[1]-p2.prev_pos[1], p2.pos[2]-p2.prev_pos[2]
                                    rvx, rvy, rvz = v2x-v1x, v2y-v1y, v2z-v1z if self.is_3d else 0.0
                                    
                                    vel_normal = rvx*nx + rvy*ny + rvz*nz
                                    if vel_normal < 0:
                                        imp = -(1.0 + bounce) * vel_normal * 0.5
                                        if not p1.is_static:
                                            p1.prev_pos[0] += nx * imp * fric; p1.prev_pos[1] += ny * imp * fric
                                            if self.is_3d: p1.prev_pos[2] += nz * imp * fric
                                        if not p2.is_static:
                                            p2.prev_pos[0] -= nx * imp * fric; p2.prev_pos[1] -= ny * imp * fric
                                            if self.is_3d: p2.prev_pos[2] -= nz * imp * fric


