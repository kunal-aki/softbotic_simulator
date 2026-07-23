import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *

from engine.camera import Camera3D
from engine.renderer import Renderer3D
from engine.world import World3D
from objects.mesh_generator import MeshGenerator3D
from objects.soft_body import SoftBody3D

class SimulationApp:
    def __init__(self, width=1280, height=720, title="BioSim 3D - Soft Robotics Studio"):
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.clock = pygame.time.Clock()

        # Input tracking
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.mouse_button = None

        # Core Engine Modules
        self.camera = Camera3D(
            target=(0.0, 1.0, 0.0), 
            distance=8.0, 
            aspect_ratio=width / height
        )
        self.world = World3D()
        self.renderer = Renderer3D(grid_size=20, grid_spacing=0.5)

    def init_pygame_gl(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        
        # Request OpenGL double buffering & depth buffer
        pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

        self.window = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )
        
        # Initialize OpenGL context state in renderer
        self.renderer.init_gl()

    def load_demo_scene(self):
        """Populates the 3D world with initial soft robotic blocks."""
        mesh_a = MeshGenerator3D.create_block_3d(
            dimensions=(3, 3, 3), 
            spacing=0.4, 
            origin=(-0.6, 0.2, -0.6)
        )
        body_a = SoftBody3D("soft_cube_1", mesh_a)
        body_a.is_actuated = True  # Enable pneumatic pulsing motion
        
        self.world.add_soft_body(body_a)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == VIDEORESIZE:
                self.width, self.height = event.w, event.h
                glViewport(0, 0, self.width, self.height)
                self.camera.aspect_ratio = self.width / max(1, self.height)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button in (1, 2, 3):  # Left, Middle, Right click
                    self.mouse_dragging = True
                    self.mouse_button = event.button
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Scroll Up
                    self.camera.zoom(0.5)
                elif event.button == 5:  # Scroll Down
                    self.camera.zoom(-0.5)

            elif event.type == MOUSEBUTTONUP:
                self.mouse_dragging = False

            elif event.type == MOUSEMOTION and self.mouse_dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.last_mouse_pos = event.pos

                if self.mouse_button == 1:  # Left Click Drag -> Orbit Camera
                    self.camera.orbit(dyaw=dx * 0.4, dpitch=-dy * 0.4)
                elif self.mouse_button == 3:  # Right Click Drag -> Pan Camera
                    self.camera.pan(dx=-dx * 0.01, dy=dy * 0.01)

    def run(self):
        self.init_pygame_gl()
        self.load_demo_scene()
        self.running = True

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Cap at 60 FPS, get delta time in seconds

            # 1. Process Window & Camera Events
            self.handle_events()

            # 2. Advance Physics & Actuation Step
            for body in self.world.soft_bodies:
                body.update_actuation(dt)
            self.world.step(dt)

            # 3. Render 3D Scene
            self.renderer.render_scene(self.camera, self.world)

            # 4. Swap OpenGL Framebuffers
            pygame.display.flip()

        pygame.quit()
        sys.exit()


