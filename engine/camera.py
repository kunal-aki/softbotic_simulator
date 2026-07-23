import numpy as np

class Camera3D:
    """3D Orbital Camera providing view/projection matrices and ray casting for UI interactions."""
    def __init__(self, target=(0.0, 1.0, 0.0), distance=8.0, yaw=45.0, pitch=25.0, fov=45.0, aspect_ratio=1.33):
        self.target = np.array(target, dtype=np.float32)
        self.distance = distance
        self.yaw = yaw
        self.pitch = pitch
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = 0.1
        self.far = 100.0

    @property
    def position(self):
        rad_yaw = np.radians(self.yaw)
        rad_pitch = np.radians(self.pitch)
        x = self.target[0] + self.distance * np.cos(rad_pitch) * np.sin(rad_yaw)
        y = self.target[1] + self.distance * np.sin(rad_pitch)
        z = self.target[2] + self.distance * np.cos(rad_pitch) * np.cos(rad_yaw)
        return np.array([x, y, z], dtype=np.float32)

    def orbit(self, dyaw, dpitch):
        self.yaw = (self.yaw + dyaw) % 360.0
        self.pitch = np.clip(self.pitch + dpitch, -89.0, 89.0)

    def zoom(self, delta):
        self.distance = np.clip(self.distance - delta, 1.0, 50.0)

    def pan(self, dx, dy):
        rad_yaw = np.radians(self.yaw)
        forward = self.target - self.position
        forward = forward / np.linalg.norm(forward)
        right = np.array([np.sin(rad_yaw - np.pi/2), 0, np.cos(rad_yaw - np.pi/2)])
        up = np.cross(right, forward)
        self.target += (right * dx + up * dy) * (self.distance * 0.05)

    def get_view_matrix(self):
        eye = self.position
        target = self.target
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        f = (target - eye)
        f /= np.linalg.norm(f)
        s = np.cross(f, up)
        s /= np.linalg.norm(s)
        u = np.cross(s, f)

        m = np.identity(4, dtype=np.float32)
        m[0, :3] = s
        m[1, :3] = u
        m[2, :3] = -f
        m[0, 3] = -np.dot(s, eye)
        m[1, 3] = -np.dot(u, eye)
        m[2, 3] = np.dot(f, eye)
        return m

    def get_projection_matrix(self):
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        m = np.zeros((4, 4), dtype=np.float32)
        m[0, 0] = f / self.aspect_ratio
        m[1, 1] = f
        m[2, 2] = (self.far + self.near) / (self.near - self.far)
        m[2, 3] = (2.0 * self.far * self.near) / (self.near - self.far)
        m[3, 2] = -1.0
        return m


