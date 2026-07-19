import math

class Obstacle:
    def __init__(self, x, y, z=0.0, shape_type="circle", r=55.0, w=180.0, h=50.0, d=150.0, angle=0.0):
        self.pos = [float(x), float(y), float(z)]
        self.type = shape_type
        self.radius = r
        self.width = w
        self.height = h
        self.depth = d
        self.angle = angle

    def resolve_collision(self, p, is_3d):
        dx = p.pos[0] - self.pos[0]
        dy = p.pos[1] - self.pos[1]
        dz = p.pos[2] - self.pos[2] if is_3d else 0.0

        if self.type == "circle":
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            min_dist = self.radius + 6.0
            if dist < min_dist and dist > 0.001:
                nx = dx / dist
                ny = dy / dist
                nz = dz / dist if is_3d else 0.0
                overlap = min_dist - dist
                
                p.pos[0] += nx * overlap
                p.pos[1] += ny * overlap
                if is_3d: 
                    p.pos[2] += nz * overlap
                    
                # High friction slide against obstacles
                p.prev_pos[0] = p.pos[0] - (p.pos[0] - p.prev_pos[0]) * 0.2
                p.prev_pos[1] = p.pos[1] - (p.pos[1] - p.prev_pos[1]) * 0.2

        elif self.type == "box":
            cos_a, sin_a = math.cos(-self.angle), math.sin(-self.angle)
            local_x = dx * cos_a - dy * sin_a
            local_y = dx * sin_a + dy * cos_a

            hw, hh, hd = self.width / 2.0 + 4.0, self.height / 2.0 + 4.0, self.depth / 2.0 + 4.0

            if abs(local_x) < hw and abs(local_y) < hh and (not is_3d or abs(dz) < hd):
                ox = hw - abs(local_x)
                oy = hh - abs(local_y)
                oz = hd - abs(dz) if is_3d else 99999.0

                if ox < oy and (not is_3d or ox < oz):
                    push_x = ox if local_x > 0 else -ox
                    push_y = 0.0
                elif oy < ox and (not is_3d or oy < oz):
                    push_x = 0.0
                    push_y = oy if local_y > 0 else -oy
                else:
                    p.pos[2] += oz if dz > 0 else -oz
                    p.prev_pos[2] = p.pos[2]
                    return

                world_push_x = push_x * math.cos(self.angle) - push_y * math.sin(self.angle)
                world_push_y = push_x * math.sin(self.angle) + push_y * math.cos(self.angle)

                p.pos[0] += world_push_x
                p.pos[1] += world_push_y
                p.prev_pos[0] = p.pos[0] - (p.pos[0] - p.prev_pos[0]) * 0.2
                p.prev_pos[1] = p.pos[1] - (p.pos[1] - p.prev_pos[1]) * 0.2


