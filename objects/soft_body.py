import math

class SoftBody:
    # Class tracking variable to ensure every soft body gets a unique identity key
    _next_id = 0

    def __init__(self, world, x, y, z=0.0, shape_type="cube", size=80.0, preset="Jello"):
        self.id = SoftBody._next_id
        SoftBody._next_id += 1
        
        self.particles = []
        self.springs = []
        self.world = world
        self.shape_type = shape_type
        self.size = size
        self.preset_name = preset
        
        presets = {
            "Jello": [800.0, 6.0, 1.0],
            "Memory Foam": [1200.0, 15.0, 1.6]
        }
        self.k, self.damping, self.mass = presets[preset]
        self.build_mesh(x, y, z)

        if not hasattr(world, 'soft_bodies'):
            world.soft_bodies = []
        world.soft_bodies.append(self)

    def build_mesh(self, x, y, z=0.0):
        self.particles.clear()
        self.springs.clear()

        if self.shape_type == "cube":
            grid = {}
            offsets = [-self.size/2, self.size/2]
            for dx in offsets:
                for dy in offsets:
                    for dz in offsets:
                        p = self.world.add_particle(x + dx, y + dy, z + dz, mass=self.mass)
                        p.body_id = self.id  # Assign parent container link
                        p.color = (138, 43, 226) if self.preset_name == "Jello" else (210, 180, 140)
                        self.particles.append(p)
                        grid[(dx, dy, dz)] = p
            keys = list(grid.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    k1, k2 = keys[i], keys[j]
                    diffs = sum(1 for c in range(3) if k1[c] != k2[c])
                    if diffs == 1:
                        self.springs.append(self.world.add_spring(grid[k1], grid[k2], k=self.k, damping=self.damping))
                    elif diffs in [2, 3]:
                        self.springs.append(self.world.add_spring(grid[k1], grid[k2], k=self.k*0.5, damping=self.damping))

        elif self.shape_type == "sphere":
            layers, segments = 4, 6
            center_p = self.world.add_particle(x, y, z, mass=self.mass * 1.5)
            center_p.body_id = self.id
            center_p.color = (255, 255, 255)
            self.particles.append(center_p)
            for i in range(1, layers):
                lat = (math.pi / layers) * i
                for j in range(segments):
                    lon = (2 * math.pi / segments) * j
                    px = x + self.size * math.sin(lat) * math.cos(lon)
                    py = y + self.size * math.cos(lat)
                    pz = z + self.size * math.sin(lat) * math.sin(lon)
                    p = self.world.add_particle(px, py, pz, mass=self.mass)
                    p.body_id = self.id
                    p.color = (0, 191, 255)
                    self.particles.append(p)
                    self.springs.append(self.world.add_spring(p, center_p, k=self.k, damping=self.damping))
            for i in range(1, len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    p1, p2 = self.particles[i], self.particles[j]
                    dist = math.sqrt(sum((p2.pos[c] - p1.pos[c])**2 for c in range(3)))
                    if dist < self.size * 1.3:
                        self.springs.append(self.world.add_spring(p1, p2, k=self.k*0.7, damping=self.damping))

        elif self.shape_type == "square":
            rows, cols = 3, 3
            spacing = self.size / 2.0
            grid = []
            for r in range(rows):
                row_particles = []
                for c in range(cols):
                    px = x + (c - 1) * spacing
                    py = y + (r - 1) * spacing
                    p = self.world.add_particle(px, py, 0.0, mass=self.mass)
                    p.body_id = self.id
                    p.color = (138, 43, 226) if self.preset_name == "Jello" else (210, 180, 140)
                    self.particles.append(p)
                    row_particles.append(p)
                grid.append(row_particles)
            for r in range(rows):
                for c in range(cols):
                    if c < cols - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r][c+1], k=self.k, damping=self.damping))
                    if r < rows - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c], k=self.k, damping=self.damping))
                    if r < rows - 1 and c < cols - 1:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c+1], k=self.k*0.5, damping=self.damping))
                    if r < rows - 1 and c > 0:
                        self.springs.append(self.world.add_spring(grid[r][c], grid[r+1][c-1], k=self.k*0.5, damping=self.damping))

        elif self.shape_type == "triangle":
            sides = 3
            center_p = self.world.add_particle(x, y, 0.0, mass=self.mass * 1.2)
            center_p.body_id = self.id
            center_p.color = (255, 255, 255)
            self.particles.append(center_p)
            perimeter = []
            for i in range(sides):
                angle = i * (2 * math.pi / sides) - math.pi / 2
                px = x + self.size * math.cos(angle)
                py = y + self.size * math.sin(angle)
                p = self.world.add_particle(px, py, 0.0, mass=self.mass)
                p.body_id = self.id
                p.color = (0, 191, 255)
                self.particles.append(p)
                perimeter.append(p)
            for i in range(sides):
                self.springs.append(self.world.add_spring(perimeter[i], perimeter[(i+1)%sides], k=self.k, damping=self.damping))
                self.springs.append(self.world.add_spring(perimeter[i], center_p, k=self.k, damping=self.damping))

    def convert_dimension(self, to_3d, cx, cy):
        avg_x = sum(p.pos[0] for p in self.particles) / len(self.particles) if self.particles else cx
        avg_y = sum(p.pos[1] for p in self.particles) / len(self.particles) if self.particles else cy
        
        for p in self.particles:
            if p in self.world.particles: self.world.particles.remove(p)
        for s in self.springs:
            if s in self.world.springs: self.world.springs.remove(s)

        if to_3d:
            self.shape_type = "cube" if self.shape_type == "square" else "sphere"
        else:
            self.shape_type = "square" if self.shape_type == "cube" else "triangle"

        self.build_mesh(avg_x, avg_y, 0.0)


