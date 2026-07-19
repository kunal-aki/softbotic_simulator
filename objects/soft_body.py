import math

# Safely check for pygame to prevent NameError if it hasn't been initialized/imported yet
try:
    import pygame
except ImportError:
    pygame = None

class SoftBody:
    _next_id = 0

    def __init__(self, world, x, y, z=0.0, shape_type="cube", size=80.0, preset="Jello"):
        self.id = SoftBody._next_id
        SoftBody._next_id += 1
       
        self.particles = []
        self.springs = []
        self.rest_offsets = []
        self.world = world
        self.shape_type = shape_type
        self.size = size
        self.preset_name = preset
       
        # Tuned spring dynamics for high elasticity and smooth movement
        presets = {
            "Jello": [450.0, 8.0, 1.0],        # Flexible & bouncier
            "Memory Foam": [850.0, 18.0, 1.4]  # Slower response, high squish
        }
        self.k, self.damping, self.mass = presets.get(preset, presets["Jello"])
       
        # --- RIGID-TO-SOFT COUPLING FEATURE ---
        self.rigid_joints = []
       
        self.build_mesh(x, y, z)
        world.soft_bodies.append(self)

    def build_mesh(self, x, y, z=0.0):
        self.particles.clear()
        self.springs.clear()
        self.rest_offsets.clear()

        if self.shape_type == "cube":
            offsets = [-self.size/2, self.size/2]
            cp = self.world.add_particle(x, y, z, mass=self.mass * 1.5)
            cp.body_id = self.id
            cp.color = (140, 50, 230)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])

            grid = []
            for dx in offsets:
                for dy in offsets:
                    for dz in offsets:
                        p = self.world.add_particle(x + dx, y + dy, z + dz, mass=self.mass)
                        p.body_id = self.id
                        p.color = (138, 43, 226)
                        self.particles.append(p)
                        self.rest_offsets.append([dx, dy, dz])
                        grid.append(p)
                        self.springs.append(self.world.add_spring(p, cp, k=self.k, damping=self.damping))

            for i in range(len(grid)):
                for j in range(i + 1, len(grid)):
                    p1, p2 = grid[i], grid[j]
                    d = math.sqrt(sum((p1.pos[c] - p2.pos[c])**2 for c in range(3)))
                    self.springs.append(self.world.add_spring(p1, p2, k=self.k * (0.8 if d < self.size * 1.1 else 0.4), damping=self.damping))

        elif self.shape_type == "pyramid":
            hw = self.size / 2.0
            local_pts = [[-hw, hw, -hw], [hw, hw, -hw], [hw, hw, hw], [-hw, hw, hw], [0.0, -hw, 0.0]]
            for pt in local_pts:
                p = self.world.add_particle(x + pt[0], y + pt[1], z + pt[2], mass=self.mass)
                p.body_id = self.id
                p.color = (230, 90, 40)
                self.particles.append(p)
                self.rest_offsets.append(pt)
            for i in range(4):
                self.springs.append(self.world.add_spring(self.particles[i], self.particles[(i+1)%4], k=self.k, damping=self.damping))
                self.springs.append(self.world.add_spring(self.particles[i], self.particles[4], k=self.k, damping=self.damping))
            self.springs.append(self.world.add_spring(self.particles[0], self.particles[2], k=self.k, damping=self.damping))
            self.springs.append(self.world.add_spring(self.particles[1], self.particles[3], k=self.k, damping=self.damping))

        elif self.shape_type == "sphere":
            layers, segments = 4, 6
            cp = self.world.add_particle(x, y, z, mass=self.mass * 2.0)
            cp.body_id = self.id
            cp.color = (255, 255, 255)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])

            for i in range(1, layers):
                lat = (math.pi / layers) * i
                for j in range(segments):
                    lon = (2 * math.pi / segments) * j
                    dx = self.size * math.sin(lat) * math.cos(lon)
                    dy = self.size * math.cos(lat)
                    dz = self.size * math.sin(lat) * math.sin(lon)
                    p = self.world.add_particle(x + dx, y + dy, z + dz, mass=self.mass)
                    p.body_id = self.id
                    p.color = (0, 191, 255)
                    self.particles.append(p)
                    self.rest_offsets.append([dx, dy, dz])
                    self.springs.append(self.world.add_spring(p, cp, k=self.k, damping=self.damping))

            for i in range(1, len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    p1, p2 = self.particles[i], self.particles[j]
                    d = math.sqrt(sum((p2.pos[c] - p1.pos[c])**2 for c in range(3)))
                    if d < self.size * 1.3:
                        self.springs.append(self.world.add_spring(p1, p2, k=self.k * 0.6, damping=self.damping))

        elif self.shape_type == "square":
            rows, cols = 3, 3
            spacing = self.size / 2.0
            grid = []
            for r in range(rows):
                row_pts = []
                for c in range(cols):
                    dx, dy = (c - 1) * spacing, (r - 1) * spacing
                    p = self.world.add_particle(x + dx, y + dy, 0.0, mass=self.mass)
                    p.body_id = self.id
                    p.color = (138, 43, 226)
                    self.particles.append(p)
                    self.rest_offsets.append([dx, dy, 0.0])
                    row_pts.append(p)
                grid.append(row_pts)
            for r in range(rows):
                for c in range(cols):
                    if c < cols - 1: self.springs.append(self.world.add_spring(grid[r][c], grid[r][c+1], k=self.k, damping=self.damping))
                    if r < rows - 1: self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c], k=self.k, damping=self.damping))
                    if r < rows - 1 and c < cols - 1: self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c+1], k=self.k, damping=self.damping))
                    if r < rows - 1 and c > 0: self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c-1], k=self.k, damping=self.damping))

        elif self.shape_type == "triangle":
            sides = 3
            cp = self.world.add_particle(x, y, 0.0, mass=self.mass * 1.5)
            cp.body_id = self.id
            cp.color = (255, 255, 255)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])
            for i in range(sides):
                angle = i * (2 * math.pi / sides) - math.pi / 2
                dx, dy = self.size * math.cos(angle), self.size * math.sin(angle)
                p = self.world.add_particle(x + dx, y + dy, 0.0, mass=self.mass)
                p.body_id = self.id
                p.color = (230, 90, 40)
                self.particles.append(p)
                self.rest_offsets.append([dx, dy, 0.0])
                self.springs.append(self.world.add_spring(p, cp, k=self.k, damping=self.damping))
            for i in range(1, sides + 1):
                self.springs.append(self.world.add_spring(self.particles[i], self.particles[1 + (i % sides)], k=self.k, damping=self.damping))

        elif self.shape_type == "circle":
            segments = 8
            cp = self.world.add_particle(x, y, 0.0, mass=self.mass * 1.5)
            cp.body_id = self.id
            cp.color = (255, 255, 255)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])
            ring = []
            for i in range(segments):
                angle = i * (2 * math.pi / segments)
                dx, dy = self.size * math.cos(angle), self.size * math.sin(angle)
                p = self.world.add_particle(x + dx, y + dy, 0.0, mass=self.mass)
                p.body_id = self.id
                p.color = (0, 191, 255)
                self.particles.append(p)
                self.rest_offsets.append([dx, dy, 0.0])
                ring.append(p)
                self.springs.append(self.world.add_spring(p, cp, k=self.k, damping=self.damping))
            for i in range(segments):
                self.springs.append(self.world.add_spring(ring[i], ring[(i+1)%segments], k=self.k, damping=self.damping))

    def get_center_of_mass(self):
        if not self.particles: return [0.0, 0.0, 0.0]
        return [sum(p.pos[c] for p in self.particles) / len(self.particles) for c in range(3)]

    def get_faces(self):
        if self.shape_type == "cube" and len(self.particles) == 9:
            return [
                [1, 2, 4, 3], [5, 6, 8, 7], [1, 2, 6, 5],
                [3, 4, 8, 7], [1, 3, 7, 5], [2, 4, 8, 6]
            ]
        elif self.shape_type == "pyramid" and len(self.particles) == 5:
            return [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
        return []

    def attach_to_rigid_body(self, rigid_body, particle_index, local_offset):
        if 0 <= particle_index < len(self.particles):
            self.rigid_joints.append({
                'rigid_body': rigid_body,
                'particle': self.particles[particle_index],
                'local_offset': local_offset
            })

    def update_rigid_constraints(self):
        for joint in self.rigid_joints:
            p = joint['particle']
            if p.is_static or getattr(p, 'is_grabbed', False):
                continue
               
            rb = joint['rigid_body']
            ox, oy, oz = joint['local_offset']
            angle = getattr(rb, 'angle', 0.0)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
           
            tx = rb.pos[0] + (ox * cos_a - oy * sin_a)
            ty = rb.pos[1] + (ox * sin_a + oy * cos_a)
            tz = rb.pos[2] + oz if len(rb.pos) > 2 else 0.0
           
            p.pos[0], p.pos[1], p.pos[2] = tx, ty, tz
            p.prev_pos[0], p.prev_pos[1], p.prev_pos[2] = tx, ty, tz

    # --- BALANCED FLEXIBLE SHAPE INTEGRITY SYSTEM ---

    def maintain_volume(self):
        """Allows realistic squishing and bending while keeping total structural shape intact."""
        if not self.particles:
            return

        self.update_rigid_constraints()
        cx, cy, cz = self.get_center_of_mass()

        # Step 1: Compute dynamic body orientation (theta)
        a00 = a01 = a10 = a11 = 0.0
        for i, p in enumerate(self.particles):
            rx, ry, _ = self.rest_offsets[i]
            dx = p.pos[0] - cx
            dy = p.pos[1] - cy
            a00 += dx * rx
            a01 += dx * ry
            a10 += dy * rx
            a11 += dy * ry

        theta = math.atan2(a10 - a01, a00 + a11)
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        # Soft restoration bias: 0.08 lets objects squish on impact, then smoothly regain shape
        restoration_stiffness = 0.08 
        min_squish_ratio = 0.35      # Prevents nodes from collapsing inside out beyond 35% radius

        # Step 2: Soft shape-restoration pass
        for i, p in enumerate(self.particles):
            # Velocity clamping to stop high-speed drag explosions across large maps
            vx = p.pos[0] - p.prev_pos[0]
            vy = p.pos[1] - p.prev_pos[1]
            max_speed = 45.0
            speed_sq = vx * vx + vy * vy
            if speed_sq > max_speed * max_speed:
                factor = max_speed / math.sqrt(speed_sq)
                p.prev_pos[0] = p.pos[0] - vx * factor
                p.prev_pos[1] = p.pos[1] - vy * factor

            if p.is_static or getattr(p, 'is_grabbed', False):
                continue

            rx, ry, rz = self.rest_offsets[i]
            rest_dist = math.sqrt(rx**2 + ry**2 + rz**2)

            # Skip center particle logic if rest offset is near zero
            if rest_dist < 0.001:
                continue

            # Rotated rest positions
            rot_rx = rx * cos_t - ry * sin_t
            rot_ry = rx * sin_t + ry * cos_t
            rot_rz = rz

            # Ideal target coordinate
            goal_x = cx + rot_rx
            goal_y = cy + rot_ry
            goal_z = cz + rot_rz if self.world.is_3d else 0.0

            # Current particle offset from center of mass
            curr_dx = p.pos[0] - cx
            curr_dy = p.pos[1] - cy
            curr_dz = p.pos[2] - cz if self.world.is_3d else 0.0
            curr_dist = math.sqrt(curr_dx**2 + curr_dy**2 + curr_dz**2)

            # Check if particle is squished past the inversion threshold
            dot_prod = (curr_dx * rot_rx) + (curr_dy * rot_ry) + (curr_dz * rot_rz)
            
            if dot_prod <= 0.0 or curr_dist < rest_dist * min_squish_ratio:
                # Emergency anti-inversion push back to safe minimum distance
                push_factor = (rest_dist * min_squish_ratio) / (curr_dist + 0.0001)
                shift_x = (cx + curr_dx * push_factor) - p.pos[0]
                shift_y = (cy + curr_dy * push_factor) - p.pos[1]
                shift_z = ((cz + curr_dz * push_factor) - p.pos[2]) if self.world.is_3d else 0.0
            else:
                # Gentle elastic force guiding node toward target shape
                shift_x = (goal_x - p.pos[0]) * restoration_stiffness
                shift_y = (goal_y - p.pos[1]) * restoration_stiffness
                shift_z = (goal_z - p.pos[2]) * restoration_stiffness if self.world.is_3d else 0.0

            # Apply Verlet-safe positional adjustments
            p.pos[0] += shift_x
            p.pos[1] += shift_y
            p.prev_pos[0] += shift_x
            p.prev_pos[1] += shift_y

            if self.world.is_3d:
                p.pos[2] += shift_z
                p.prev_pos[2] += shift_z

    def convert_dimension(self, to_3d, cx, cy):
        com = self.get_center_of_mass()
        for p in list(self.particles):
            if p in self.world.particles: self.world.particles.remove(p)
        for s in list(self.springs):
            if s in self.world.springs: self.world.springs.remove(s)

        if to_3d:
            mapping = {"square": "cube", "triangle": "pyramid", "circle": "sphere"}
            self.shape_type = mapping.get(self.shape_type, "cube")
        else:
            mapping = {"cube": "square", "pyramid": "triangle", "sphere": "circle"}
            self.shape_type = mapping.get(self.shape_type, "square")

        self.build_mesh(com[0], com[1], com[2] if to_3d else 0.0)


