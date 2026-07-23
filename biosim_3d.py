"""
BioSim 3D - Standalone Single-File Application
Goal: 3D CAD-like workspace with perspective camera, 3D spatial grid, and object placement.
Controls:
  - Right Click + Drag : Orbit Camera (Pitch & Yaw)
  - Middle Click + Drag: Pan Camera (X & Y translation)
  - Scroll Wheel       : Zoom In / Out
  - SPACE              : Toggle Auto-Rotation
  - A                  : Add a 3D Cube at current camera target
  - C                  : Clear all placed 3D Cubes
"""

import math
import pygame
from pygame.locals import *

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    raise ImportError("PyOpenGL is required to run this 3D workspace. Install via 'pip install PyOpenGL'.")

# ==============================================================================
# 1. CONFIGURATION & LAYOUT CONSTANTS
# ==============================================================================
WIDTH = 1280
HEIGHT = 720
TITLE = "BioSim 3D - CAD & Soft Robotics Workspace"
FPS = 60

COLOR_TEXT = (220, 225, 230)
COLOR_TEXT_DIM = (140, 145, 155)

# ==============================================================================
# 2. 3D ORBIT CAMERA
# ==============================================================================
class Camera3D:
    def __init__(self):
        self.distance = 12.0
        self.pitch = 25.0  # Rotation around X-axis
        self.yaw = 45.0    # Rotation around Y-axis
        self.target = [0.0, 0.0, 0.0]  # Point the camera looks at

    def update_projection(self, aspect_ratio):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def apply_view(self):
        glLoadIdentity()
        
        # Convert polar orientation (distance, pitch, yaw) to 3D Cartesian coords
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)

        cam_x = self.target[0] + self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        cam_y = self.target[1] + self.distance * math.sin(rad_pitch)
        cam_z = self.target[2] + self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)

        gluLookAt(
            cam_x, cam_y, cam_z,
            self.target[0], self.target[1], self.target[2],
            0.0, 1.0, 0.0
        )

    def orbit(self, dx, dy):
        self.yaw += dx * 0.4
        self.pitch += dy * 0.4
        # Clamp pitch to prevent flipping upside down
        self.pitch = max(-89.0, min(89.0, self.pitch))

    def pan(self, dx, dy):
        # Move target point horizontally and vertically relative to screen orientation
        rad_yaw = math.radians(self.yaw)
        speed = self.distance * 0.0015
        
        self.target[0] -= (dx * math.cos(rad_yaw) + dy * math.sin(rad_yaw)) * speed
        self.target[2] -= (-dx * math.sin(rad_yaw) + dy * math.cos(rad_yaw)) * speed

    def zoom(self, factor):
        self.distance = max(2.0, min(50.0, self.distance * factor))

# ==============================================================================
# 3. 3D SCENE OBJECTS & RENDERER
# ==============================================================================
class Cube3D:
    def __init__(self, x=0.0, y=0.5, z=0.0, size=1.0):
        self.pos = [x, y, z]
        self.size = size

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        s = self.size / 2.0

        # Define 8 corners of the cube
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s,  s], [s, -s,  s], [s, s,  s], [-s, s,  s]
        ]

        # Define 6 faces (each made of 4 vertices)
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 3, 7, 4), (1, 2, 6, 5)
        ]

        # Draw Solid Faces (Silicone Light-Blue Tint)
        glColor4f(0.2, 0.6, 0.9, 0.85)
        glBegin(GL_QUADS)
        for face in faces:
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
        glEnd()

        # Draw Wireframe Overlay (Darker Outline)
        glColor3f(0.0, 0.2, 0.4)
        glLineWidth(2.0)
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        glBegin(GL_LINES)
        for edge in edges:
            for vertex_idx in edge:
                glVertex3fv(vertices[vertex_idx])
        glEnd()

        glPopMatrix()


def draw_grid_and_axes(grid_size=20, spacing=1.0):
    # Draw Ground Grid Plane (XZ Plane)
    glLineWidth(1.0)
    glColor3f(0.2, 0.23, 0.28)
    glBegin(GL_LINES)
    half = (grid_size * spacing) / 2.0
    for i in range(grid_size + 1):
        pos = -half + (i * spacing)
        # X-Parallel Lines
        glVertex3f(-half, 0.0, pos)
        glVertex3f(half, 0.0, pos)
        # Z-Parallel Lines
        glVertex3f(pos, 0.0, -half)
        glVertex3f(pos, 0.0, half)
    glEnd()

    # Draw 3D Origin Axes (Red=X, Green=Y, Blue=Z)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    # X Axis (Red)
    glColor3f(0.9, 0.2, 0.2)
    glVertex3f(0, 0, 0)
    glVertex3f(3.0, 0, 0)
    # Y Axis (Green)
    glColor3f(0.2, 0.9, 0.2)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 3.0, 0)
    # Z Axis (Blue)
    glColor3f(0.2, 0.4, 0.9)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 3.0)
    glEnd()

# ==============================================================================
# 4. MAIN APPLICATION
# ==============================================================================
class App3D:
    def __init__(self):
        pygame.init()
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.camera = Camera3D()
        self.camera.update_projection(WIDTH / float(HEIGHT))

        # Enable 3D Depth Testing & Transparency
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.08, 0.09, 0.11, 1.0)

        self.cubes = [Cube3D(0.0, 0.5, 0.0)]
        self.running = True
        self.auto_rotate = False
        self.orbiting = False
        self.panning = False
        self.last_mouse = (0, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_SPACE:
                    self.auto_rotate = not self.auto_rotate
                elif event.key == K_a:
                    # Place a new 3D cube directly at the target location
                    tx, ty, tz = self.camera.target
                    self.cubes.append(Cube3D(tx, ty + 0.5, tz))
                elif event.key == K_c:
                    self.cubes.clear()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 3:  # Right Click
                    self.orbiting = True
                    self.last_mouse = event.pos
                elif event.button == 2:  # Middle Click
                    self.panning = True
                    self.last_mouse = event.pos
                elif event.button == 4:  # Scroll Up
                    self.camera.zoom(0.9)
                elif event.button == 5:  # Scroll Down
                    self.camera.zoom(1.1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 3:
                    self.orbiting = False
                elif event.button == 2:
                    self.panning = False

            elif event.type == MOUSEMOTION:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]

                if self.orbiting:
                    self.camera.orbit(dx, dy)
                elif self.panning:
                    self.camera.pan(dx, dy)

                self.last_mouse = event.pos

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.auto_rotate:
            self.camera.orbit(0.5, 0)

        self.camera.apply_view()

        # Render 3D Environment
        draw_grid_and_axes()

        # Render Placed 3D Objects
        for cube in self.cubes:
            cube.draw()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.render()
        pygame.quit()


if __name__ == "__main__":
    app = App3D()
    app.run()

