import pygame
from OpenGL.GL import *
from ui.buttons import UIButton
from ui.overlays import UIOverlay
from objects.mesh_generator import MeshGenerator3D
from objects.soft_body import SoftBody3D

class UIManager:
    def __init__(self, app):
        self.app = app
        self.selected_object_id = None
        self.placement_type = "Cube Voxel"  # Active selection
        self.buttons = []
        
        # Initialize Pygame Font for OpenGL Texture rendering
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.text_textures = {}
        
        self.setup_ui_layout()

    def setup_ui_layout(self):
        """Constructs all UI interactive screen buttons and layout anchors."""
        self.buttons.clear()

        # --- Top Toolbar Buttons ---
        self.buttons.append(UIButton((15, 10, 110, 32), "Cube Block", lambda: self.set_placement("Cube Voxel")))
        self.buttons.append(UIButton((135, 10, 110, 32), "Actuator", lambda: self.set_placement("Actuator")))
        self.buttons.append(UIButton((255, 10, 120, 32), "Spawn Part", self.spawn_active_object))

        # --- Top Right Control Actions ---
        self.buttons.append(UIButton((self.app.width - 215, 10, 95, 32), "Clear World", self.clear_world, color=(0.5, 0.2, 0.2, 0.8)))
        self.buttons.append(UIButton((self.app.width - 110, 10, 95, 32), "Toggle Motion", self.toggle_actuation, color=(0.2, 0.5, 0.3, 0.8)))

    def set_placement(self, obj_type):
        self.placement_type = obj_type

    def toggle_actuation(self):
        for body in self.app.world.soft_bodies:
            body.is_actuated = not body.is_actuated

    def clear_world(self):
        self.app.world.soft_bodies.clear()
        self.selected_object_id = None

    def spawn_active_object(self):
        """Spawns chosen soft robotic block into the center of the 3D map floor."""
        count = len(self.app.world.soft_bodies) + 1
        obj_id = f"soft_part_{count}"
        
        offset = (count % 4) * 0.7
        mesh = MeshGenerator3D.create_block_3d(
            dimensions=(3, 3, 3),
            spacing=0.4,
            origin=(-0.6 + offset, 0.2, -0.6)
        )
        body = SoftBody3D(obj_id, mesh)
        
        if self.placement_type == "Actuator":
            body.is_actuated = True
            body.color = (0.9, 0.4, 0.2, 0.85)

        self.app.world.add_soft_body(body)
        self.selected_object_id = obj_id

    def handle_event(self, event):
        """Processes mouse interactions over UI components."""
        if event.type == pygame.MOUSEMOTION:
            for b in self.buttons:
                b.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.buttons:
                if b.handle_click(event.pos):
                    return True  # Consume event so camera does not orbit
        return False

    def draw_text_gl(self, text, x, y, color=(255, 255, 255)):
        """Utility to render Pygame text directly onto an OpenGL 2D screen quad."""
        surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(surface, "RGBA", True)
        w, h = surface.get_width(), surface.get_height()

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([texture])

    def draw_3d_map_grid(self, size=10, step=1):
        """Renders a 3D floor map grid with major/minor gridlines and origin axes."""
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)

        # 1. Base Grid Lines
        glBegin(GL_LINES)
        for i in range(-size, size + 1, step):
            if i == 0:
                continue  # Skip center lines to draw highlighted axes instead
            
            # Subtle grid line color
            glColor4f(0.25, 0.28, 0.35, 0.5)
            
            # Lines along X-axis
            glVertex3f(-size, 0.0, i)
            glVertex3f(size, 0.0, i)
            
            # Lines along Z-axis
            glVertex3f(i, 0.0, -size)
            glVertex3f(i, 0.0, size)
        glEnd()

        # 2. Origin Center Axes (X = Red, Y = Green, Z = Blue)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # X Axis
        glColor3f(0.8, 0.2, 0.2)
        glVertex3f(-size, 0.0, 0.0)
        glVertex3f(size, 0.0, 0.0)

        # Y Axis (Height indicator at origin)
        glColor3f(0.2, 0.8, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)

        # Z Axis
        glColor3f(0.2, 0.4, 0.8)
        glVertex3f(0.0, 0.0, -size)
        glVertex3f(0.0, 0.0, size)
        glEnd()

        glLineWidth(1.0)

    def render_2d_ui(self, width, height):
        """Main rendering pass for screen HUD overlay."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)  # 2D Orthographic view
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # 1. Draw Top Toolbar Banner Panel
        UIOverlay.draw_panel(0, 0, width, 52, bg_color=(0.11, 0.12, 0.15, 0.9))

        # 2. Draw Inspector Side Panel (Left)
        UIOverlay.draw_panel(10, 62, 220, 240, bg_color=(0.12, 0.14, 0.17, 0.85))

        # Render Inspector Info Labels
        self.draw_text_gl("OBJECT INSPECTOR", 20, 75, (200, 210, 225))
        self.draw_text_gl(f"Selected Tool: {self.placement_type}", 20, 105, (160, 175, 190))
        self.draw_text_gl(f"Total Objects: {len(self.app.world.soft_bodies)}", 20, 130, (160, 175, 190))
        
        selected_txt = self.selected_object_id if self.selected_object_id else "None"
        self.draw_text_gl(f"Active Part: {selected_txt}", 20, 155, (160, 175, 190))

        # 3. Draw Buttons and text labels
        for b in self.buttons:
            b.draw(self.font)
            # Center text inside button bounds
            tx = b.rect.x + (b.rect.width // 2) - 30
            ty = b.rect.y + 8
            self.draw_text_gl(b.text, tx, ty, (240, 240, 245))

        # Restore original 3D render matrices
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


