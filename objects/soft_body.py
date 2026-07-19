import math

class SoftBody:
    def __init__(self, world, x, y, z=0.0, shape_type="cube", size=80.0, preset="Jello"):
        self.particles = []
        self.springs = []
        self.world = world
        self.shape_type = shape_type
        
        # Core material parameter configurations
        presets = {
            "Jello": [800.0, 6.0, 1.0],
            "Memory Foam": [1200.0, 15.0, 1.6]
        }
        k, damping, mass = presets[preset]

        if shape_type == "cube":
            # Generate 8 vertices of a 3D structural cube mesh
            grid = {}
            offsets = [-size/2, size/2]
            idx = 0
            for dx in offsets:
                for dy in offsets:
                    for dz in offsets:
                        p = world.add_particle(x + dx, y + dy, z + dz, mass=mass)
                        p.color = (138, 43, 226) if preset == "Jello" else (210, 180, 140)
                        self.particles.append(p)
                        grid[(dx, dy, dz)] = p

            # Interconnect all 3D cube outer borders and diagonal bracing
            keys = list(grid.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    k1, k2 = keys[i], keys[j]
                    # Determine architectural matrix connections based on coordinate offsets
                    diffs = sum(1 for c in range(3) if k1[c] != k2[c])
                    if diffs == 1: # Structural Edge
                        self.springs.append(world.add_spring(grid[k1], grid[k2], k=k, damping=damping))
                    elif diffs in [2, 3]: # Cross Shearing Structural Bracing
                        self.springs.append(world.add_spring(grid[k1], grid[k2], k=k*0.5, damping=damping))

        elif shape_type == "sphere":
            # Generate a 3D structural UV Sphere lattice network
            layers = 4
            segments = 6
            center_p = world.add_particle(x, y, z, mass=mass*1.5)
            center_p.color = (255, 255, 255)
            self.particles.append(center_p)

            for i in range(1, layers):
                lat = (math.pi / layers) * i
                for j in range(segments):
                    lon = (2 * math.pi / segments) * j
                    px = x + size * math.sin(lat) * math.cos(lon)
                    py = y + size * math.cos(lat)
                    pz = z + size * math.sin(lat) * math.sin(lon)
                    
                    p = world.add_particle(px, py, pz, mass=mass)
                    p.color = (0, 191, 255)
                    self.particles.append(p)
                    
                    # Connect to core node structure
                    self.springs.append(world.add_spring(p, center_p, k=k, damping=damping))

            # Cross-link nearby structural boundary layers
            for i in range(1, len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    p1, p2 = self.particles[i], self.particles[j]
                    dx = p2.pos[0] - p1.pos[0]
                    dy = p2.pos[1] - p1.pos[1]
                    dz = p2.pos[2] - p1.pos[2]
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < size * 1.3:
                        self.springs.append(world.add_spring(p1, p2, k=k*0.7, damping=damping))

        if not hasattr(world, 'soft_bodies'):
            world.soft_bodies = []
        world.soft_bodies.append(self)


