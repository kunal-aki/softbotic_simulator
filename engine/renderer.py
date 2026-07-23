import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Renderer3D:
    """Renders the 3D Grid, Soft Robotic Objects, and Assembly Visuals preserving original aesthetic UI."""
    
    def __init__(self, window=None, grid_size=20, grid_spacing=0.5):
        """
        Accepts optional parameters so passing arguments like `self.window` or `app` 
        will not trigger a positional argument mismatch error.
        """
        self.window = window
        self.grid_size = grid_size
        self.grid_spacing = grid_spacing

    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        # Setup aesthetic soft lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, (10.0, 20.0, 10.0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.95, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.35, 1.0))

    def render_grid_3d(self):
        """Renders the 3D Assembly Grid floor (XZ) with elevation/spatial guide ticks."""
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)
        
        half_size = (self.grid_size * self.grid_spacing) / 2.0
        
        glBegin(GL_LINES)
        # Main Floor Grid (XZ Plane)
        for i in range(-self.grid_size // 2, self.grid_size // 2 + 1):
            pos = i * self.grid_spacing
            
            # Major vs Minor grid colors for clean aesthetics
            if i == 0:
                glColor4f(0.8, 0.2, 0.2, 0.6) # X-Axis Highlight
            else:
                glColor4f(0.25, 0.28, 0.35, 0.3)
                
            glVertex3f(pos, 0.0, -half_size)
            glVertex3f(pos, 0.0, half_size)

            if i == 0:
                glColor4f(0.2, 0.2, 0.8, 0.6) # Z-Axis Highlight
            else:
                glColor4f(0.25, 0.28, 0.35, 0.3)
                
            glVertex3f(-half_size, 0.0, pos)
            glVertex3f(half_size, 0.0, pos)

        # 3D Height Guide Posts at corner bounds
        glColor4f(0.4, 0.4, 0.5, 0.2)
        for cx in [-half_size, half_size]:
            for cz in [-half_size, half_size]:
                glVertex3f(cx, 0.0, cz)
                glVertex3f(cx, half_size, cz)
        glEnd()
        
        glEnable(GL_LIGHTING)

    def render_soft_body_3d(self, soft_body, is_selected=False):
        """Renders 3D soft-body objects with pneumatic aesthetics and spring connections."""
        positions = soft_body.positions
        
        # 1. Render 3D Mass Springs
        glDisable(GL_LIGHTING)
        glLineWidth(2.0 if not is_selected else 3.5)
        glBegin(GL_LINES)
        for spring in soft_body.springs:
            p1, p2 = positions[spring['node1']], positions[spring['node2']]
            if is_selected:
                glColor4f(1.0, 0.8, 0.2, 0.9)
            elif spring['type'] == 'structural':
                glColor4f(soft_body.color[0], soft_body.color[1], soft_body.color[2], 0.8)
            else:
                glColor4f(0.5, 0.5, 0.6, 0.3) # Subtle cross-bracing
            glVertex3fv(p1)
            glVertex3fv(p2)
        glEnd()
        
        # 2. Render 3D Soft Voxel Nodes
        glEnable(GL_LIGHTING)
        for i, pos in enumerate(positions):
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            if is_selected:
                glColor4f(1.0, 0.5, 0.0, 1.0)
            else:
                glColor4f(0.9, 0.9, 0.95, 0.9)
            
            # Render node sphere/cube voxel point
            quad = gluNewQuadric()
            gluSphere(quad, 0.05, 8, 8)
            gluDeleteQuadric(quad)
            glPopMatrix()

    def render_scene(self, camera, world, ui_manager=None):
        """Main display routine: sets up 3D view and renders grid + assembled soft bodies."""
        glClearColor(0.12, 0.13, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup camera matrices
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(camera.get_projection_matrix().T)
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(camera.get_view_matrix().T)
        
        # Render 3D spatial grid & ground plane
        self.render_grid_3d()
        
        # Render all assembled soft bodies
        for body in world.soft_bodies:
            is_selected = (ui_manager and ui_manager.selected_object_id == body.id)
            self.render_soft_body_3d(body, is_selected=is_selected)


