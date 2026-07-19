import math
from physics.particle import Particle
from physics.spring import Spring

class World:
    def __init__(self, width=1100, height=750):
        self.sim_width = 2000
        self.sim_height = 1400
        self.sim_depth = 600.0
        
        self.particles = []
        self.springs = []
        self.soft_bodies = []
        self.obstacles = []
        self.gravity = [0.0, 550.0, 0.0] 
        self.is_3d = True  

    def add_particle(self, x, y, z=0.0, mass=1.0):
        p = Particle(x, y, z, mass)
        p.body_id = -1  # Default fallback identity tag
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
        for sb in self.soft_bodies:
            if particle in sb.particles: sb.particles.remove(particle)
            sb.springs = [s for s in sb.springs if s.p1 != particle and s.p2 != particle]
        self.soft_bodies = [sb for sb in self.soft_bodies if len(sb.particles) > 0]

    def remove_obstacle(self, obs):
        if obs in self.obstacles:
            self.obstacles.remove(obs)

    def step(self, dt, substeps=4):
        sdt = dt / substeps
        for _ in range(substeps):
            for p in self.particles:
                p.apply_force((self.gravity[0] * p.mass, self.gravity[1] * p.mass, self.gravity[2] * p.mass))
            
            for s in self.springs: s.update()
            for p in self.particles: p.update(sdt)
            
            for obs in self.obstacles:
                for p in self.particles: 
                    obs.resolve_collision(p, self.is_3d)
                    
            self.resolve_constraints()
            self.resolve_soft_body_collisions()

    def resolve_constraints(self):
        floor, ceiling = self.sim_height - 100, 100
        right_wall, left_wall = self.sim_width - 100, 100
        front_wall, back_wall = self.sim_depth, -self.sim_depth
        bounce = 0.22

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

    def resolve_soft_body_collisions(self):
        """Processes bounce impulses exclusively between nodes of differing body IDs."""
        num_particles = len(self.particles)
        if num_particles < 2: return
        
        collision_radius = 48.0 if self.is_3d else 36.0
        min_dist_sq = collision_radius * collision_radius
        bounce_restitution = 0.45  
        friction_damp = 0.92       

        for i in range(num_particles):
            p1 = self.particles[i]
            for j in range(i + 1, num_particles):
                p2 = self.particles[j]
                
                # Verify particles belong to separate objects before running bounce calculations
                if p1.body_id == p2.body_id or p1.body_id == -1 or p2.body_id == -1:
                    continue

                dx = p2.pos[0] - p1.pos[0]
                dy = p2.pos[1] - p1.pos[1]
                dz = p2.pos[2] - p1.pos[2] if self.is_3d else 0.0
                dist_sq = dx*dx + dy*dy + dz*dz
                
                if dist_sq < min_dist_sq and dist_sq > 0.001:
                    dist = math.sqrt(dist_sq)
                    nx = dx / dist
                    ny = dy / dist
                    nz = dz / dist if self.is_3d else 0.0
                    
                    overlap = (collision_radius - dist) * 0.5
                    
                    if not p1.is_static:
                        p1.pos[0] -= nx * overlap
                        p1.pos[1] -= ny * overlap
                        if self.is_3d: p1.pos[2] -= nz * overlap
                        
                    if not p2.is_static:
                        p2.pos[0] += nx * overlap
                        p2.pos[1] += ny * overlap
                        if self.is_3d: p2.pos[2] += nz * overlap

                    v1x, v1y, v1z = p1.pos[0] - p1.prev_pos[0], p1.pos[1] - p1.prev_pos[1], p1.pos[2] - p1.prev_pos[2]
                    v2x, v2y, v2z = p2.pos[0] - p2.prev_pos[0], p2.pos[1] - p2.prev_pos[1], p2.pos[2] - p2.prev_pos[2]
                    
                    rvx = v2x - v1x
                    rvy = v2y - v1y
                    rvz = v2z - v1z if self.is_3d else 0.0
                    
                    vel_along_normal = rvx * nx + rvy * ny + rvz * nz
                    
                    if vel_along_normal < 0:
                        impulse_scalar = -(1.0 + bounce_restitution) * vel_along_normal * 0.5
                        ix, iy, iz = nx * impulse_scalar, ny * impulse_scalar, nz * impulse_scalar
                        
                        if not p1.is_static:
                            p1.prev_pos[0] += ix * friction_damp
                            p1.prev_pos[1] += iy * friction_damp
                            if self.is_3d: p1.prev_pos[2] += iz * friction_damp
                            
                        if not p2.is_static:
                            p2.prev_pos[0] -= ix * friction_damp
                            p2.prev_pos[1] -= iy * friction_damp
                            if self.is_3d: p2.prev_pos[2] -= iz * friction_damp


