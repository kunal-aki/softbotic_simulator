import math

class Obstacle:
    def __init__(self, x, y, z=0.0, shape_type="circle", r=55.0, w=180.0, h=50.0, d=150.0):
        self.pos = [float(x), float(y), float(z)]
        self.type = shape_type  # "circle" (Sphere in 3D) or "box" (Column in 3D)
        self.radius = r
        self.width = w
        self.height = h
        self.depth = d  # Z-axis size configuration for 3D state

    def resolve_collision(self, p, is_3d):
        dx = p.pos[0] - self.pos[0]
        dy = p.pos[1] - self.pos[1]
        dz = p.pos[2] - self.pos[2] if is_3d else 0.0
        
        if self.type == "circle":
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            min_dist = self.radius + 4.0  # Safe boundary padding
            if dist < min_dist and dist > 0.001:
                nx, ny, nz = dx / dist, dy / dist, dz / dist if is_3d else 0.0
                overlap = min_dist - dist
                
                p.pos[0] += nx * overlap
                p.pos[1] += ny * overlap
                if is_3d: p.pos[2] += nz * overlap
                
                # Apply localized boundary reflection dampening
                p.prev_pos[0] = p.pos[0] + (p.pos[0] - p.prev_pos[0]) * 0.25
                p.prev_pos[1] = p.pos[1] + (p.pos[1] - p.prev_pos[1]) * 0.25
                if is_3d: p.prev_pos[2] = p.pos[2] + (p.pos[2] - p.prev_pos[2]) * 0.25

        elif self.type == "box":
            hw, hh, hd = self.width / 2.0, self.height / 2.0, self.depth / 2.0
            
            # Check overlap logic
            in_x = abs(dx) < hw
            in_y = abs(dy) < hh
            in_z = abs(dz) < hd if is_3d else True
            
            if in_x and in_y and in_z:
                ox = hw - abs(dx)
                oy = hh - abs(dy)
                oz = hd - abs(dz) if is_3d else 99999.0
                
                # Push back along the shallowest penetration vector axis
                if ox < oy and (not is_3d or ox < oz):
                    p.pos[0] += ox if dx > 0 else -ox
                    p.prev_pos[0] = p.pos[0]
                elif oy < ox and (not is_3d or oy < oz):
                    p.pos[1] += oy if dy > 0 else -oy
                    p.prev_pos[1] = p.pos[1]
                elif is_3d:
                    p.pos[2] += oz if dz > 0 else -oz
                    p.prev_pos[2] = p.pos[2]


