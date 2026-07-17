import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.particle import Particle
from physics.spring import Spring

class SoftBody:
    def __init__(self, world, x, y, rows=4, cols=4, spacing=45.0, k=700.0, damping=5.0):
        self.particles = []
        self.springs = []
        self.grid = []
        self.world = world
        
        # 1. Build Node Coordinate Matrix
        for r in range(rows):
            row_particles = []
            for c in range(cols):
                px = x + c * spacing
                py = y + r * spacing
                particle = world.add_particle(px, py, mass=1.0)
                # Green top row, cyan body
                particle.color = (57, 255, 20) if r == 0 else (0, 191, 178) 
                self.particles.append(particle)
                row_particles.append(particle)
            self.grid.append(row_particles)

        # 2. Map the boundary particles in clockwise order for pressure tracking
        self.boundary = []
        for c in range(cols): self.boundary.append(self.grid[0][c])          
        for r in range(1, rows): self.boundary.append(self.grid[r][cols-1])   
        for c in range(cols-2, -1, -1): self.boundary.append(self.grid[rows-1][c]) 
        for r in range(rows-2, 0, -1): self.boundary.append(self.grid[r][0])   

        # Target structural volume area
        self.rest_volume = (cols - 1) * spacing * (rows - 1) * spacing
        self.pressure_coefficient = 3.5 

        # 3. Interlink Nodes Structurally
        for r in range(rows):
            for c in range(cols):
                p_current = self.grid[r][c]

                # Horizontals (Rest Length = spacing)
                if c < cols - 1:
                    self.springs.append(world.add_spring(p_current, self.grid[r][c+1], k=k, damping=damping))

                # Verticals (Rest Length = spacing)
                if r < rows - 1:
                    self.springs.append(world.add_spring(p_current, self.grid[r+1][c], k=k, damping=damping))

                # 🎯 Diagonal Right (Rest Length = spacing * sqrt(2))
                if r < rows - 1 and c < cols - 1:
                    s = world.add_spring(p_current, self.grid[r+1][c+1], k=k, damping=damping)
                    s.rest_length = spacing * math.sqrt(2.0)
                    s.color = (0, 80, 90)
                    self.springs.append(s)

                # 🎯 Diagonal Left (Rest Length = spacing * sqrt(2))
                if r < rows - 1 and c > 0:
                    s = world.add_spring(p_current, self.grid[r+1][c-1], k=k, damping=damping)
                    s.rest_length = spacing * math.sqrt(2.0)
                    s.color = (0, 80, 90)
                    self.springs.append(s)

        # 4. Core Anti-Fold Bracing Struts
        for i in range(len(self.boundary)):
            opposite_index = (i + len(self.boundary) // 2) % len(self.boundary)
            p1 = self.boundary[i]
            p2 = self.boundary[opposite_index]
            
            s = world.add_spring(p1, p2, k=k * 0.5, damping=damping)
            # Calculate actual distance for internal rest link
            dx = p2.pos[0] - p1.pos[0]
            dy = p2.pos[1] - p1.pos[1]
            s.rest_length = math.sqrt(dx*dx + dy*dy)
            s.color = (30, 60, 90)
            self.springs.append(s)

        # 5. AUTO-SNAP ANCHORS
        snap_radius = 40.0
        for p in self.particles:
            for existing_p in world.particles:
                if existing_p.is_static and existing_p not in self.particles:
                    dx = p.pos[0] - existing_p.pos[0]
                    dy = p.pos[1] - existing_p.pos[1]
                    if math.sqrt(dx*dx + dy*dy) <= snap_radius:
                        p.pos = [existing_p.pos[0], existing_p.pos[1]]
                        p.prev_pos = [existing_p.pos[0], existing_p.pos[1]]
                        s = world.add_spring(existing_p, p, k=800.0, damping=5.0)
                        s.color = (0, 229, 255)
                        self.springs.append(s)
                    
        if not hasattr(world, 'soft_bodies'):
            world.soft_bodies = []
        world.soft_bodies.append(self)

    def apply_pressure(self):
        """Calculates current 2D volume (area) and pushes outward gently."""
        if len(self.boundary) < 3:
            return

        current_volume = 0.0
        for i in range(len(self.boundary)):
            p1 = self.boundary[i]
            p2 = self.boundary[(i + 1) % len(self.boundary)]
            current_volume += (p1.pos[0] * p2.pos[1]) - (p2.pos[0] * p1.pos[1])
        current_volume = abs(current_volume) * 0.5

        if current_volume == 0: 
            return

        volume_diff = self.rest_volume - current_volume
        if volume_diff > 0: 
            pressure_force = min(volume_diff * self.pressure_coefficient, 1200.0)

            for i in range(len(self.boundary)):
                p_prev = self.boundary[i - 1]
                p_curr = self.boundary[i]
                p_next = self.boundary[(i + 1) % len(self.boundary)]

                dx = p_next.pos[0] - p_prev.pos[0]
                dy = p_next.pos[1] - p_prev.pos[1]
                
                nx = -dy
                ny = dx
                length = math.sqrt(nx*nx + ny*ny)
                
                if length > 0:
                    nx /= length
                    ny /= length
                    p_curr.apply_force((nx * pressure_force, ny * pressure_force))


