import math

class Spring:
    def __init__(self, p1, p2, k=500.0, damping=5.0):
        self.p1 = p1
        self.p2 = p2
        self.k = k
        self.damping = damping
        
        # Calculate initial 3D Euclidean distance rest length
        dx = self.p2.pos[0] - self.p1.pos[0]
        dy = self.p2.pos[1] - self.p1.pos[1]
        dz = self.p2.pos[2] - self.p1.pos[2]
        self.rest_length = math.sqrt(dx*dx + dy*dy + dz*dz)

    def update(self):
        dx = self.p2.pos[0] - self.p1.pos[0]
        dy = self.p2.pos[1] - self.p1.pos[1]
        dz = self.p2.pos[2] - self.p1.pos[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)

        if dist == 0: return

        # 3D Normalizing Vector strings
        nx, ny, nz = dx / dist, dy / dist, dz / dist
        displacement = dist - self.rest_length

        # 3D Velocity vectors
        v1x = self.p1.pos[0] - self.p1.prev_pos[0]
        v1y = self.p1.pos[1] - self.p1.prev_pos[1]
        v1z = self.p1.pos[2] - self.p1.prev_pos[2]

        v2x = self.p2.pos[0] - self.p2.prev_pos[0]
        v2y = self.p2.pos[1] - self.p2.prev_pos[1]
        v2z = self.p2.pos[2] - self.p2.prev_pos[2]

        # Relative velocity calculation
        rvx = v2x - v1x
        rvy = v2y - v1y
        rvz = v2z - v1z

        # Hooke's Law + 3D Viscous Damping
        spring_force = displacement * self.k
        damping_force = (rvx * nx + rvy * ny + rvz * nz) * self.damping
        total_force = spring_force + damping_force

        fx = nx * total_force
        fy = ny * total_force
        fz = nz * total_force

        self.p1.apply_force((fx, fy, fz))
        self.p2.apply_force((-fx, -fy, -fz))


