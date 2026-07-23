import numpy as np

class World3D:
    """3D Physics and Assembly Container for Soft Robotic Objects."""
    def __init__(self, gravity=(0.0, -9.81, 0.0)):
        self.gravity = np.array(gravity, dtype=np.float32)
        self.soft_bodies = []
        self.floor_height = 0.0
        self.weld_threshold = 0.15 # Max distance to automatically attach/assemble parts

    def add_soft_body(self, soft_body):
        soft_body.snap_to_3d_grid()
        self.soft_bodies.append(soft_body)
        self.check_and_weld_assemblies(soft_body)

    def check_and_weld_assemblies(self, target_body):
        """Assembles adjacent 3D objects together by fusing overlapping nodes."""
        for body in self.soft_bodies:
            if body.id == target_body.id:
                continue
            
            # Check for close nodes and snap/weld them together
            for i, p1 in enumerate(target_body.positions):
                for j, p2 in enumerate(body.positions):
                    dist = np.linalg.norm(p1 - p2)
                    if dist < self.weld_threshold:
                        # Fuse positions for a seamless structural assembly
                        avg_pos = (p1 + p2) * 0.5
                        target_body.positions[i] = avg_pos
                        body.positions[j] = avg_pos

    def step(self, dt):
        """Advances 3D mass-spring-damper physics simulation."""
        for body in self.soft_bodies:
            body.forces[:] = 0.0
            
            # Apply Gravity
            for i in range(len(body.positions)):
                body.forces[i] += self.gravity * body.masses[i]
                
            # Apply Spring Forces in 3D
            for spring in body.springs:
                i, j = spring['node1'], spring['node2']
                p1, p2 = body.positions[i], body.positions[j]
                v1, v2 = body.velocities[i], body.velocities[j]
                
                delta_p = p1 - p2
                dist = np.linalg.norm(delta_p) + 1e-6
                dir_p = delta_p / dist
                
                rest_len = spring.get('current_rest_length', spring['rest_length'])
                
                # Hooke's Law + Damping
                f_spring = -body.material['stiffness'] * (dist - rest_len) * dir_p
                f_damping = -body.material['damping'] * np.dot(v1 - v2, dir_p) * dir_p
                
                total_f = f_spring + f_damping
                body.forces[i] += total_f
                body.forces[j] -= total_f
                
            # Integration & 3D Floor Collisions
            for i in range(len(body.positions)):
                acc = body.forces[i] / body.masses[i]
                body.velocities[i] += acc * dt
                body.positions[i] += body.velocities[i] * dt
                
                # Ground Collision (XZ Floor)
                if body.positions[i][1] < self.floor_height:
                    body.positions[i][1] = self.floor_height
                    body.velocities[i][1] *= -0.2 # Bounce damping
                    body.velocities[i][0] *= 0.8  # Friction
                    body.velocities[i][2] *= 0.8


