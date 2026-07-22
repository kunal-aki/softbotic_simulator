"""
BioSim v2.0 - Object Architecture & Scene Graph
Defines SceneObjects, Particles, Springs, SoftBodies, and Verlet physics solvers.
"""

import math
import json
from engine.config import VIEWPORT_X, VIEWPORT_Y, MATERIALS


class SceneObject:
    """Base Object Interface for CAD Entity Management."""

    def __init__(self, name="Object", x=0.0, y=0.0):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.rotation = 0.0
        self.scale = 1.0
        self.material_name = "Silicone"
        self.visible = True
        self.selected = False

    def get_material(self):
        return MATERIALS.get(self.material_name, MATERIALS["Silicone"])

    def set_material(self, mat_name):
        if mat_name in MATERIALS:
            self.material_name = mat_name
            self.apply_material_properties()

    def apply_material_properties(self):
        pass

    def get_aabb(self):
        return (self.x - 10, self.y - 10, self.x + 10, self.y + 10)

    def contains_point(self, wx, wy):
        min_x, min_y, max_x, max_y = self.get_aabb()
        return min_x <= wx <= max_x and min_y <= wy <= max_y

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "scale": self.scale,
            "material_name": self.material_name,
            "visible": self.visible
        }


class Particle(SceneObject):

    def __init__(self, x, y, name="Particle", mass=1.0, pinned=False):
        super().__init__(name=name, x=x, y=y)
        self.old_x = float(x)
        self.old_y = float(y)
        self.mass = float(mass)
        self.pinned = pinned
        self.radius = 8.0
        self.apply_material_properties()

    def apply_material_properties(self):
        mat = self.get_material()
        self.mass = (mat["density"] / 1000.0)

    def update_physics(self, dt, gravity=980.0):
        if self.pinned or not self.visible:
            return

        mat = self.get_material()
        damping = mat["damping"]

        vx = (self.x - self.old_x) * damping
        vy = (self.y - self.old_y) * damping

        self.old_x = self.x
        self.old_y = self.y

        self.x += vx
        self.y += vy + gravity * (dt * dt)

    def resolve_ground(self, ground_y=600.0):
        if self.pinned or not self.visible:
            return
        if self.y + self.radius > ground_y:
            self.y = ground_y - self.radius
            self.old_y = self.y + (self.y - self.old_y) * 0.4

    def get_aabb(self):
        r = self.radius
        return (self.x - r, self.y - r, self.x + r, self.y + r)

    def contains_point(self, wx, wy):
        dx = self.x - wx
        dy = self.y - wy
        return (dx * dx + dy * dy) <= (self.radius * self.radius * 2.2)

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "type": "Particle",
            "pinned": self.pinned,
            "mass": self.mass
        })
        return d


class SpringConstraint:

    def __init__(self, p1, p2, stiffness=0.5):
        self.p1 = p1
        self.p2 = p2
        self.stiffness = stiffness
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        self.rest_length = math.hypot(dx, dy)

    def resolve(self):
        if not self.p1.visible or not self.p2.visible:
            return

        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        delta = (dist - self.rest_length) / dist
        nx = dx * delta * 0.5 * self.stiffness
        ny = dy * delta * 0.5 * self.stiffness

        if not self.p1.pinned:
            self.p1.x += nx
            self.p1.y += ny
        if not self.p2.pinned:
            self.p2.x -= nx
            self.p2.y -= ny


class SoftBodyMesh(SceneObject):

    def __init__(self, x, y, name="SoftBody Mesh", shape_type="rect", width=80.0, height=80.0, rows=3, cols=3):
        super().__init__(name=name, x=x, y=y)
        self.shape_type = shape_type
        self.width = float(width)
        self.height = float(height)
        self.rows = rows
        self.cols = cols
        self.particles = []
        self.springs = []
        self.build_mesh()

    def build_mesh(self):
        self.particles.clear()
        self.springs.clear()

        if self.shape_type == "rect":
            step_x = self.width / max(1, self.cols - 1)
            step_y = self.height / max(1, self.rows - 1)
            grid = []

            for r in range(self.rows):
                row_nodes = []
                for c in range(self.cols):
                    px = self.x - (self.width / 2.0) + (c * step_x)
                    py = self.y - (self.height / 2.0) + (r * step_y)
                    p = Particle(px, py, name=f"{self.name}_Node_{r}_{c}")
                    p.material_name = self.material_name
                    self.particles.append(p)
                    row_nodes.append(p)
                grid.append(row_nodes)

            stiff = self.get_material()["stiffness"]
            for r in range(self.rows):
                for c in range(self.cols):
                    if c + 1 < self.cols:
                        self.springs.append(SpringConstraint(grid[r][c], grid[r][c + 1], stiff))
                    if r + 1 < self.rows:
                        self.springs.append(SpringConstraint(grid[r][c], grid[r + 1][c], stiff))
                    if r + 1 < self.rows and c + 1 < self.cols:
                        self.springs.append(SpringConstraint(grid[r][c], grid[r + 1][c + 1], stiff))
                        self.springs.append(SpringConstraint(grid[r + 1][c], grid[r][c + 1], stiff))

        elif self.shape_type == "circle":
            center = Particle(self.x, self.y, name=f"{self.name}_Center")
            center.material_name = self.material_name
            self.particles.append(center)

            num_outer = 8
            radius = self.width / 2.0
            stiff = self.get_material()["stiffness"]
            outer_nodes = []

            for i in range(num_outer):
                angle = (2.0 * math.pi / num_outer) * i
                px = self.x + radius * math.cos(angle)
                py = self.y + radius * math.sin(angle)
                p = Particle(px, py, name=f"{self.name}_Rim_{i}")
                p.material_name = self.material_name
                self.particles.append(p)
                outer_nodes.append(p)
                self.springs.append(SpringConstraint(center, p, stiff))

            for i in range(num_outer):
                next_p = outer_nodes[(i + 1) % num_outer]
                self.springs.append(SpringConstraint(outer_nodes[i], next_p, stiff))

    def apply_material_properties(self):
        stiff = self.get_material()["stiffness"]
        for p in self.particles:
            p.set_material(self.material_name)
        for s in self.springs:
            s.stiffness = stiff

    def rotate(self, angle_delta):
        self.rotation += angle_delta
        cos_a = math.cos(angle_delta)
        sin_a = math.sin(angle_delta)
        cx, cy = self.x, self.y

        for p in self.particles:
            dx = p.x - cx
            dy = p.y - cy
            p.x = cx + (dx * cos_a - dy * sin_a)
            p.y = cy + (dx * sin_a + dy * cos_a)
            p.old_x = p.x
            p.old_y = p.y

    def apply_scale(self, factor):
        if self.scale * factor < 0.2 or self.scale * factor > 5.0:
            return
        self.scale *= factor
        cx, cy = self.x, self.y

        for p in self.particles:
            p.x = cx + (p.x - cx) * factor
            p.y = cy + (p.y - cy) * factor
            p.old_x = p.x
            p.old_y = p.y

        for s in self.springs:
            s.rest_length *= factor

    def get_aabb(self):
        if not self.particles:
            return super().get_aabb()
        min_x = min(p.x for p in self.particles)
        max_x = max(p.x for p in self.particles)
        min_y = min(p.y for p in self.particles)
        max_y = max(p.y for p in self.particles)
        return (min_x, min_y, max_x, max_y)

    def contains_point(self, wx, wy):
        min_x, min_y, max_x, max_y = self.get_aabb()
        return (min_x - 10) <= wx <= (max_x + 10) and (min_y - 10) <= wy <= (max_y + 10)

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "type": "SoftBodyMesh",
            "shape_type": self.shape_type,
            "width": self.width,
            "height": self.height,
            "rows": self.rows,
            "cols": self.cols
        })
        return d


class Scene:
    def __init__(self):
        self.objects = []
        self.springs = []
        self.paused = True
        self.gravity = 980.0
        self.ground_y = 600.0

    def update(self, dt):
        if self.paused:
            return

        dt_val = min(float(dt), 0.033)

        for obj in self.objects:
            if isinstance(obj, Particle):
                obj.update_physics(dt_val, self.gravity)
            elif isinstance(obj, SoftBodyMesh):
                for p in obj.particles:
                    p.update_physics(dt_val, self.gravity)

        for _ in range(5):
            for spring in self.springs:
                spring.resolve()
            for obj in self.objects:
                if isinstance(obj, SoftBodyMesh):
                    for spring in obj.springs:
                        spring.resolve()

        for obj in self.objects:
            if isinstance(obj, Particle):
                obj.resolve_ground(self.ground_y)
            elif isinstance(obj, SoftBodyMesh):
                for p in obj.particles:
                    p.resolve_ground(self.ground_y)

    def draw(self, renderer, camera):
        cam_x = camera.x
        cam_y = camera.y
        zoom = camera.zoom

        to_screen = lambda wx, wy: (
            int((wx + cam_x) * zoom) + VIEWPORT_X,
            int((wy + cam_y) * zoom) + VIEWPORT_Y
        )

        # Ground Plane Line
        screen_ground_y = int((self.ground_y + cam_y) * zoom) + VIEWPORT_Y
        renderer.draw_line((80, 85, 95), (VIEWPORT_X, screen_ground_y), (VIEWPORT_X + 2500, screen_ground_y), width=2)

        # Standalone Spring Constraints
        for spring in self.springs:
            if spring.p1.visible and spring.p2.visible:
                s1 = to_screen(spring.p1.x, spring.p1.y)
                s2 = to_screen(spring.p2.x, spring.p2.y)
                renderer.draw_line((180, 200, 230), s1, s2, width=max(1, int(2 * zoom)))

        # Render Scene Objects
        for obj in self.objects:
            if not obj.visible:
                continue

            if isinstance(obj, Particle):
                sp = to_screen(obj.x, obj.y)
                mat_color = obj.get_material()["color"]
                color = (255, 70, 70) if obj.pinned else mat_color
                renderer.draw_circle(color, sp, int(obj.radius * zoom))

            elif isinstance(obj, SoftBodyMesh):
                mat_color = obj.get_material()["color"]
                for spring in obj.springs:
                    s1 = to_screen(spring.p1.x, spring.p1.y)
                    s2 = to_screen(spring.p2.x, spring.p2.y)
                    renderer.draw_line((120, 130, 145), s1, s2, width=max(1, int(1.5 * zoom)))

                for p in obj.particles:
                    sp = to_screen(p.x, p.y)
                    renderer.draw_circle(mat_color, sp, int(4 * zoom))

    def pick_particle(self, world_pos):
        wx, wy = world_pos
        for obj in reversed(self.objects):
            if isinstance(obj, Particle) and obj.contains_point(wx, wy):
                return obj
            elif isinstance(obj, SoftBodyMesh):
                for p in reversed(obj.particles):
                    if p.contains_point(wx, wy):
                        return p
        return None

    def pick_object(self, world_pos):
        wx, wy = world_pos
        for obj in reversed(self.objects):
            if obj.contains_point(wx, wy):
                return obj
        return None

    def add_particle(self, x, y, pinned=False):
        name = f"Particle_{len(self.objects) + 1}"
        p = Particle(x, y, name=name, pinned=pinned)
        self.objects.append(p)
        return p

    def add_soft_body(self, x, y, shape_type="rect", width=80.0, height=80.0):
        name = f"{shape_type.capitalize()}Mesh_{len(self.objects) + 1}"
        body = SoftBodyMesh(x, y, name=name, shape_type=shape_type, width=width, height=height)
        self.objects.append(body)
        return body

    def add_spring(self, p1, p2):
        if p1 and p2 and p1 != p2:
            s = SpringConstraint(p1, p2)
            self.springs.append(s)
            return s
        return None

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            self.springs = [s for s in self.springs if s.p1 != obj and s.p2 != obj]

    def save_to_file(self, filename="scene.json"):
        data = {
            "gravity": self.gravity,
            "ground_y": self.ground_y,
            "objects": [obj.to_dict() for obj in self.objects]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename="scene.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            self.objects.clear()
            self.springs.clear()

            self.gravity = data.get("gravity", 980.0)
            self.ground_y = data.get("ground_y", 600.0)

            for item in data.get("objects", []):
                obj_type = item.get("type")
                if obj_type == "Particle":
                    p = self.add_particle(item["x"], item["y"], pinned=item.get("pinned", False))
                    p.name = item.get("name", p.name)
                    p.set_material(item.get("material_name", "Silicone"))
                    p.visible = item.get("visible", True)

                elif obj_type == "SoftBodyMesh":
                    body = self.add_soft_body(
                        item["x"], item["y"],
                        shape_type=item.get("shape_type", "rect"),
                        width=item.get("width", 80.0),
                        height=item.get("height", 80.0)
                    )
                    body.name = item.get("name", body.name)
                    body.set_material(item.get("material_name", "Silicone"))
                    body.visible = item.get("visible", True)
            return True
        except Exception:
            return False


