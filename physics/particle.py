class Particle:
    def __init__(self, x, y, z=0.0, mass=1.0, is_static=False):
        # 3D Vector coordinates
        self.pos = [float(x), float(y), float(z)]
        self.prev_pos = [float(x), float(y), float(z)]
        self.acc = [0.0, 0.0, 0.0]
        
        self.mass = mass
        self.is_static = is_static
        self.color = (0, 191, 178)

    def apply_force(self, force):
        if self.is_static: return
        self.acc[0] += force[0] / self.mass
        self.acc[1] += force[1] / self.mass
        self.acc[2] += force[2] / self.mass

    def update(self, dt):
        if self.is_static: return
        
        # Verlet Integration handling x, y, and z dimensions
        temp_x = self.pos[0]
        temp_y = self.pos[1]
        temp_z = self.pos[2]

        self.pos[0] += (self.pos[0] - self.prev_pos[0]) + self.acc[0] * dt * dt
        self.pos[1] += (self.pos[1] - self.prev_pos[1]) + self.acc[1] * dt * dt
        self.pos[2] += (self.pos[2] - self.prev_pos[2]) + self.acc[2] * dt * dt

        self.prev_pos[0] = temp_x
        self.prev_pos[1] = temp_y
        self.prev_pos[2] = temp_z

        # Reset forces
        self.acc = [0.0, 0.0, 0.0]


