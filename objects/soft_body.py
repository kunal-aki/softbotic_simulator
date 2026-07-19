import math

try:
    import pygame
except ImportError:
    pygame = None

class SoftBody:
    next_id = 0

    PRESETS = {
        "Jello": {"k": 600.0, "damping": 12.0, "mass": 1.0, "pressure": 15.0},
        "Water Balloon": {"k": 350.0, "damping": 8.0, "mass": 0.7, "pressure": 30.0},
        "Memory Foam": {"k": 900.0, "damping": 25.0, "mass": 1.3, "pressure": 0.0},
        "Rubber": {"k": 1200.0, "damping": 20.0, "mass": 1.1, "pressure": 0.0}
    }

    def __init__(self, world, x, y, z=0.0, shape_type="cube", size=80.0, preset="Jello"):
        self.id = SoftBody.next_id
        SoftBody.next_id += 1
        self.particles = []
        self.springs = []
        self.rest_offsets = []
        self.world = world
        self.shape_type = shape_type
        self.size = size
        self.preset_name = preset

        p_data = self.PRESETS.get(preset, self.PRESETS["Jello"])
        self.k = p_data["k"]
        self.damping = p_data["damping"]
        self.mass = p_data["mass"]
        self.pressure_coeff = p_data["pressure"]

        self.build_mesh(x, y, z)
        world.soft_bodies.append(self)

    def build_mesh(self, x, y, z=0.0):
        self.particles.clear()
        self.springs.clear()
        self.rest_offsets.clear()

        if self.shape_type == "cube":
            offsets = [-self.size / 2.0, self.size / 2.0]
            cp = self.world.add_particle(x, y, z, mass=self.mass * 1.2)
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
                    d = math.sqrt(sum((p1.pos[c] - p2.pos[c]) ** 2 for c in range(3)))
                    self.springs.append(self.world.add_spring(p1, p2, k=self.k * (0.9 if d < self.size * 1.1 else 0.6), damping=self.damping))

        elif self.shape_type == "pyramid":
            hw = self.size / 2.0
            local_pts = [[-hw, hw, hw], [hw, hw, -hw], [hw, hw, hw], [-hw, hw, -hw], [0.0, -hw, 0.0]]
            for pt in local_pts:
                p = self.world.add_particle(x + pt[0], y + pt[1], z + pt[2], mass=self.mass)
                p.body_id = self.id
                p.color = (230, 90, 40)
                self.particles.append(p)
                self.rest_offsets.append(pt)
            for i in range(4):
                self.springs.append(self.world.add_spring(self.particles[i], self.particles[(i + 1) % 4], k=self.k, damping=self.damping))
                self.springs.append(self.world.add_spring(self.particles[i], self.particles[4], k=self.k, damping=self.damping))
            self.springs.append(self.world.add_spring(self.particles[0], self.particles[2], k=self.k, damping=self.damping))
            self.springs.append(self.world.add_spring(self.particles[1], self.particles[3], k=self.k, damping=self.damping))

        elif self.shape_type == "triangle":
            hw = self.size / 2.0
            h = (math.sqrt(3) / 2.0) * self.size
            local_pts = [[-hw, h / 3.0, 0.0], [hw, h / 3.0, 0.0], [0.0, -2.0 * h / 3.0, 0.0]]
            
            cp = self.world.add_particle(x, y, 0.0, mass=self.mass * 1.2)
            cp.body_id = self.id
            cp.color = (240, 140, 40)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])

            ring = []
            for pt in local_pts:
                p = self.world.add_particle(x + pt[0], y + pt[1], 0.0, mass=self.mass)
                p.body_id = self.id
                p.color = (230, 90, 40)
                self.particles.append(p)
                self.rest_offsets.append(pt)
                ring.append(p)
                self.springs.append(self.world.add_spring(p, cp, k=self.k, damping=self.damping))
            
            for i in range(3):
                self.springs.append(self.world.add_spring(ring[i], ring[(i + 1) % 3], k=self.k, damping=self.damping))

        elif self.shape_type == "sphere":
            layers, segments = 4, 6
            cp = self.world.add_particle(x, y, z, mass=self.mass * 1.5)
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
                    if c < cols - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r][c + 1], k=self.k, damping=self.damping))
                    if r < rows - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r + 1][c], k=self.k, damping=self.damping))
                    if r < rows - 1 and c < cols - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r + 1][c + 1], k=self.k * 0.8, damping=self.damping))
                    if r < rows - 1 and c > 0:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r + 1][c - 1], k=self.k * 0.8, damping=self.damping))

        elif self.shape_type == "circle":
            segments = 12
            cp = self.world.add_particle(x, y, 0.0, mass=self.mass * 1.5)
            cp.body_id = self.id
            cp.color = (255, 255, 255)
            self.particles.append(cp)
            self.rest_offsets.append([0.0, 0.0, 0.0])
            ring = []
            for i in range(segments):
                angle = (2 * math.pi / segments) * i
                dx = self.size * math.cos(angle)
                dy = self.size * math.sin(angle)
                p = self.world.add_particle(x + dx, y + dy, 0.0, mass=self.mass)
                p.body_id = self.id
                p.color = (0, 191, 255)
                self.particles.append(p)
                ring.append(p)
                self.rest_offsets.append([dx, dy, 0.0])
                # Direct central struts
                self.springs.append(self.world.add_spring(p, cp, k=self.k * 1.5, damping=self.damping))
            
            # Rigid internal cross-bracing
            for i in range(segments):
                self.springs.append(self.world.add_spring(ring[i], ring[(i + 1) % segments], k=self.k, damping=self.damping))
                self.springs.append(self.world.add_spring(ring[i], ring[(i + 2) % segments], k=self.k * 0.8, damping=self.damping))
                self.springs.append(self.world.add_spring(ring[i], ring[(i + segments // 2) % segments], k=self.k * 0.6, damping=self.damping))

    def move_body_by_delta(self, dx, dy, dz=0.0):
        # Translates the whole structure together when grabbed to preserve geometry
        for p in self.particles:
            p.pos[0] += dx
            p.pos[1] += dy
            p.pos[2] += dz
            p.prev_pos[0] += dx
            p.prev_pos[1] += dy
            p.prev_pos[2] += dz

    def apply_internal_pressure(self):
        if self.pressure_coeff <= 0.0 or self.shape_type not in ("circle", "sphere") or len(self.particles) < 4:
            return

        ring_pts = self.particles[1:]
        n = len(ring_pts)
        
        curr_area = 0.0
        for i in range(n):
            p1 = ring_pts[i]
            p2 = ring_pts[(i + 1) % n]
            curr_area += (p1.pos[0] * p2.pos[1]) - (p2.pos[0] * p1.pos[1])
        curr_area = abs(curr_area) * 0.5

        target_area = math.pi * (self.size ** 2)
        p_force = (target_area - curr_area) * self.pressure_coeff * 0.005

        for i in range(n):
            p1 = ring_pts[i]
            p2 = ring_pts[(i + 1) % n]
            dx = p2.pos[0] - p1.pos[0]
            dy = p2.pos[1] - p1.pos[1]
            dist = math.hypot(dx, dy) + 0.0001
            nx, ny = -dy / dist, dx / dist
            
            fx, fy = nx * p_force * 0.5, ny * p_force * 0.5
            p1.apply_force((fx, fy, 0.0))
            p2.apply_force((fx, fy, 0.0))

    def get_center_of_mass(self):
        if not self.particles: 
            return [0.0, 0.0, 0.0]
        return [sum(p.pos[c] for p in self.particles) / len(self.particles) for c in range(3)]

    def maintain_volume(self):
        if not self.particles: 
            return
        cx, cy, cz = self.get_center_of_mass()

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
        cost, sint = math.cos(theta), math.sin(theta)

        restoration_stiffness = 0.08  # Stronger shape recovery

        for i, p in enumerate(self.particles):
            if p.is_static:
                continue

            rx, ry, rz = self.rest_offsets[i]
            rot_rx = rx * cost - ry * sint
            rot_ry = rx * sint + ry * cost
            rot_rz = rz

            goal_x = cx + rot_rx
            goal_y = cy + rot_ry
            goal_z = cz + rot_rz if self.world.is_3d else 0.0

            shift_x = (goal_x - p.pos[0]) * restoration_stiffness
            shift_y = (goal_y - p.pos[1]) * restoration_stiffness
            
            p.pos[0] += shift_x
            p.pos[1] += shift_y
            p.prev_pos[0] += shift_x
            p.prev_pos[1] += shift_y

            if self.world.is_3d:
                shift_z = (goal_z - p.pos[2]) * restoration_stiffness
                p.pos[2] += shift_z
                p.prev_pos[2] += shift_z

    def convert_dimension(self, to_3d, cx, cy):
        com = self.get_center_of_mass()
        for p in list(self.particles):
            if p in self.world.particles: 
                self.world.particles.remove(p)
        for s in list(self.springs):
            if s in self.world.springs: 
                self.world.springs.remove(s)

        if to_3d:
            mapping = {"square": "cube", "triangle": "pyramid", "circle": "sphere"}
            self.shape_type = mapping.get(self.shape_type, "cube")
        else:
            mapping = {"cube": "square", "pyramid": "triangle", "sphere": "circle"}
            self.shape_type = mapping.get(self.shape_type, "square")

        self.build_mesh(com[0], com[1], com[2] if to_3d else 0.0)


