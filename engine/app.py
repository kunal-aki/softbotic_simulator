import pygame
from engine.config import *
from engine.renderer import Renderer
from engine.camera import Camera
from engine.world import World
from objects.soft_body import SoftBody

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE + ' v0.4 — Soft Body Workspace')
        
        self.width = WIDTH
        self.height = HEIGHT
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 14)       # Scaled down to prevent text clipping
        self.font_bold = pygame.font.SysFont('consolas', 14, bold=True)
        
        self.renderer = Renderer(self.screen)
        self.camera = Camera()
        self.world = World()
        self.running = True
        self.dragging = False
        self.last_mouse = (0, 0)
        self.selected_particle = None
        self.start_link_particle = None  # Tracks custom spring wiring interactions

        # Spawn initial baseline dynamic soft body (Uniform spacing=45.0)
        SoftBody(self.world, x=400, y=150, rows=4, cols=4, spacing=45.0, k=600.0, damping=3.0)

    def draw_grid(self):
        spacing = GRID_SIZE * self.camera.zoom
        if spacing < 10: 
            return
        ox = (self.camera.x * self.camera.zoom) % spacing
        oy = (self.camera.y * self.camera.zoom) % spacing
        
        x = -spacing
        while x < self.width + spacing:
            self.renderer.draw_line(GRID_COLOR, (x + ox, 0), (x + ox, self.height))
            x += spacing
        y = -spacing
        while y < self.height + spacing:
            self.renderer.draw_line(GRID_COLOR, (0, y + oy), (self.width, y + oy))
            y += spacing

    def draw_ui(self):
        fps = self.clock.get_fps()
        world_mouse = self.camera.screen_to_world(pygame.mouse.get_pos())
        
        # 1. Left Stats Panel
        self.renderer.draw_text(self.font_bold, "SYSTEM STATUS", ACCENT_COLOR, (15, 15))
        self.renderer.draw_text(self.font, f"FPS:   {fps:.1f}", TEXT_COLOR, (15, 35))
        self.renderer.draw_text(self.font, f"ZOOM:  {self.camera.zoom:.2f}x", TEXT_COLOR, (15, 55))
        self.renderer.draw_text(self.font, f"NODES: {len(self.world.particles)}", TEXT_COLOR, (15, 75))
        self.renderer.draw_text(self.font, f"LINKS: {len(self.world.springs)}", TEXT_COLOR, (15, 95))
        self.renderer.draw_text(self.font, f"MOUSE: ({int(world_mouse[0])}, {int(world_mouse[1])})", TEXT_COLOR, (15, 115))

        # 2. Right "Directions & Keybinds" Panel (Widened context card container)
        panel_width = 380  
        panel_height = 260
        panel_x = self.width - panel_width - 15
        panel_y = 15
        
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BORDER, (panel_x, panel_y, panel_width, panel_height), 1, border_radius=6)

        self.renderer.draw_text(self.font_bold, "WORKSPACE CONTROLS", ACCENT_COLOR, (panel_x + 15, panel_y + 15))
        
        controls = [
            ("L-Click", "Spawn Individual Node"),
            ("Shift+L-Click", "Spawn Static Anchor"),
            ("Drag Anchor", "Wire Spring Link to Node"),
            ("S Key", "Spawn 4x4 Soft Body Cube"),
            ("D Key", "Delete Node under mouse"),
            ("Scroll Wheel", "Zoom Viewport In/Out"),
            ("Space+L-Click", "Pan Viewport (Trackpad)"),
            ("ESC Key", "Exit Simulator Safely")
        ]
        
        curr_y = panel_y + 45
        for key, desc in controls:
            self.renderer.draw_text(self.font_bold, key, ACCENT_COLOR, (panel_x + 15, curr_y))
            self.renderer.draw_text(self.font, desc, TEXT_COLOR, (panel_x + 145, curr_y))
            curr_y += 24

    def update(self):
        dt = 1.0 / FPS
        # Sub-stepping loop runs physics iterations multiple times per frame for stiffness
        for _ in range(3):
            self.world.update(dt / 3.0)

    def render(self):
        self.renderer.clear(BACKGROUND)
        self.draw_grid()
        self.world.draw(self.renderer, self.camera)
        
        # Draw dynamic real-time spring line guide while actively wiring
        if self.start_link_particle:
            start_screen = self.camera.world_to_screen(self.start_link_particle.pos)
            end_screen = pygame.mouse.get_pos()
            self.renderer.draw_line((0, 229, 255), start_screen, end_screen, 2)
            
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.renderer.screen = self.screen
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  
                        self.running = False
                        
                    elif event.key == pygame.K_s:
                        world_pos = self.camera.screen_to_world(pygame.mouse.get_pos())
                        # Explicitly matching structural configurations to uniform spacing=45.0
                        SoftBody(self.world, x=world_pos[0]-90, y=world_pos[1]-90, rows=4, cols=4, spacing=45.0, k=600.0, damping=3.0)
                        
                    elif event.key == pygame.K_d:
                        # Clean Node deletion tracker logic
                        world_pos = self.camera.screen_to_world(pygame.mouse.get_pos())
                        target = None
                        grab_threshold = 25.0
                        for p in self.world.particles:
                            dx = p.pos[0] - world_pos[0]
                            dy = p.pos[1] - world_pos[1]
                            if (dx*dx + dy*dy) < grab_threshold * grab_threshold:
                                target = p
                                break
                        if target:
                            self.world.remove_particle(target)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    world_pos = self.camera.screen_to_world(event.pos)
                    
                    if event.button == 1:  # Left Click
                        if keys[pygame.K_SPACE]:
                            self.dragging = True
                            self.last_mouse = event.pos
                        else:
                            grab_threshold = 20.0
                            clicked_particle = None
                            for p in self.world.particles:
                                dx = p.pos[0] - world_pos[0]
                                dy = p.pos[1] - world_pos[1]
                                if (dx*dx + dy*dy) < grab_threshold * grab_threshold:
                                    clicked_particle = p
                                    break
                            
                            if clicked_particle:
                                # Start spring wiring if it's a static anchor node
                                if clicked_particle.is_static:
                                    self.start_link_particle = clicked_particle
                                else:
                                    self.selected_particle = clicked_particle
                            else:
                                is_static = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                                self.world.add_particle(world_pos[0], world_pos[1], is_static=is_static)
                        
                    elif event.button == 2:
                        self.dragging = True
                        self.last_mouse = event.pos
                    elif event.button == 4:
                        self.camera.zoom_in()
                    elif event.button == 5:
                        self.camera.zoom_out()
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Process connection structural mapping if link dragging is active
                        if self.start_link_particle:
                            world_pos = self.camera.screen_to_world(event.pos)
                            grab_threshold = 20.0
                            target_particle = None
                            for p in self.world.particles:
                                if p != self.start_link_particle:
                                    dx = p.pos[0] - world_pos[0]
                                    dy = p.pos[1] - world_pos[1]
                                    if (dx*dx + dy*dy) < grab_threshold * grab_threshold:
                                        target_particle = p
                                        break
                            
                            if target_particle:
                                s = self.world.add_spring(self.start_link_particle, target_particle, k=600.0, damping=3.0)
                                s.color = (0, 229, 255) # Custom structural cyan accent color link
                        
                        self.selected_particle = None
                        self.start_link_particle = None
                        self.dragging = False
                    if event.button == 2:
                        self.dragging = False
                    
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse[0]
                        dy = event.pos[1] - self.last_mouse[1]
                        self.camera.move(dx, dy)
                        self.last_mouse = event.pos
                    elif self.selected_particle:
                        world_mouse = self.camera.screen_to_world(event.pos)
                        self.selected_particle.pos = [world_mouse[0], world_mouse[1]]
                        self.selected_particle.prev_pos = [world_mouse[0], world_mouse[1]]

            self.update()
            self.render()

        pygame.quit()


