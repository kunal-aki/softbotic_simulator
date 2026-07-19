import pygame
import math
from engine.config import *
from engine.renderer import Renderer
from engine.camera import Camera
from engine.world import World
from objects.soft_body import SoftBody
from objects.obstacle import Obstacle

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE + ' v0.8 — Master Physics Sandbox')
        
        self.width, self.height = WIDTH, HEIGHT
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 13)       
        self.font_bold = pygame.font.SysFont('consolas', 13, bold=True)
        
        self.renderer = Renderer(self.screen)
        self.camera = Camera()
        self.world = World()
        self.running = True
        self.dragging = False
        self.last_mouse = (0, 0)
        self.selected_particle = None
        self.spawn_structured = True

        self.knife_active = False
        self.knife_start = (0, 0)

        self.material_presets = ["Jello", "Water Balloon", "Memory Foam"]
        self.current_preset_idx = 0

        self.world_bounds = [-2000.0, 2000.0, -2000.0, self.world.floor_y]

        self.world.obstacles.append(Obstacle(300, 420, "circle", r=45.0))
        self.world.obstacles.append(Obstacle(550, 480, "box", w=160.0, h=40.0))
        
        SoftBody(self.world, 400, 150, "square", size=90.0, preset=self.get_current_preset(), structured=self.spawn_structured)

    def get_current_preset(self):
        return self.material_presets[self.current_preset_idx]

    def line_intersects(self, a, b, c, d):
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)

    def process_continuous_deletion(self, world_pos):
        """Erases elements instantly whenever the D key is actively held down."""
        # 1. Check for Particles under the mouse brush radius
        target_particle = None
        for p in self.world.particles:
            dx, dy = p.pos[0] - world_pos[0], p.pos[1] - world_pos[1]
            if (dx*dx + dy*dy) < 900.0:  # 30px brush radius size
                target_particle = p
                break
        
        if target_particle:
            self.world.remove_particle(target_particle)
            return

        # 2. Check for environment obstacles under mouse
        target_obstacle = None
        for obs in self.world.obstacles:
            if obs.type == "circle":
                dx, dy = obs.pos[0] - world_pos[0], obs.pos[1] - world_pos[1]
                if (dx*dx + dy*dy) < (obs.radius * obs.radius):
                    target_obstacle = obs
                    break
            elif obs.type == "box":
                half_w = obs.width / 2.0
                half_h = obs.height / 2.0
                if (world_pos[0] >= obs.pos[0] - half_w and world_pos[0] <= obs.pos[0] + half_w and
                    world_pos[1] >= obs.pos[1] - half_h and world_pos[1] <= obs.pos[1] + half_h):
                    target_obstacle = obs
                    break
                    
        if target_obstacle in self.world.obstacles: 
            self.world.obstacles.remove(target_obstacle)

    def draw_grid(self):
        spacing = GRID_SIZE * self.camera.zoom
        if spacing < 10: return
        ox, oy = (self.camera.x * self.camera.zoom) % spacing, (self.camera.y * self.camera.zoom) % spacing
        x = -spacing
        while x < self.width + spacing:
            self.renderer.draw_line(GRID_COLOR, (x + ox, 0), (x + ox, self.height))
            x += spacing
        y = -spacing
        while y < self.height + spacing:
            self.renderer.draw_line(GRID_COLOR, (0, y + oy), (self.width, y + oy))
            y += spacing

    def draw_world_border(self):
        bx_min, bx_max, by_min, by_max = self.world_bounds
        tl = self.camera.world_to_screen((bx_min, by_min))
        tr = self.camera.world_to_screen((bx_max, by_min))
        bl = self.camera.world_to_screen((bx_min, by_max))
        br = self.camera.world_to_screen((bx_max, by_max))
        border_color = (230, 50, 50)
        self.renderer.draw_line(border_color, tl, tr, 3)
        self.renderer.draw_line(border_color, tr, br, 3)
        self.renderer.draw_line(border_color, br, bl, 3)
        self.renderer.draw_line(border_color, bl, tl, 3)

    def draw_ui(self):
        fps = self.clock.get_fps()
        self.renderer.draw_text(self.font_bold, "SYSTEM STATUS", ACCENT_COLOR, (15, 15))
        self.renderer.draw_text(self.font, f"FPS:   {fps:.1f}", TEXT_COLOR, (15, 35))
        self.renderer.draw_text(self.font, f"ZOOM:  {self.camera.zoom:.2f}x", TEXT_COLOR, (15, 55))
        self.renderer.draw_text(self.font, f"BODIES: {len(self.world.soft_bodies)}", TEXT_COLOR, (15, 75))
        
        mode_str = "STRUCTURED CORE (ON)" if self.spawn_structured else "UNSTRUCTURED (OFF)"
        self.renderer.draw_text(self.font, f"CORE:  {mode_str}", (0, 255, 150) if self.spawn_structured else (255, 150, 0), (15, 95))
        self.renderer.draw_text(self.font, f"MAT:   {self.get_current_preset().upper()}", (255, 215, 0), (15, 115))

        panel_width, panel_height = 420, 360
        panel_x, panel_y = self.width - panel_width - 15, 15
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BORDER, (panel_x, panel_y, panel_width, panel_height), 1, border_radius=6)
        
        self.renderer.draw_text(self.font_bold, "WORKSPACE CONTROLS", ACCENT_COLOR, (panel_x + 15, panel_y + 15))
        controls = [
            ("S Key", "Spawn Squishy Square"),
            ("T Key", "Spawn Squishy Triangle"),
            ("P Key", "Spawn Squishy Pentagon"),
            ("1 Key", "Spawn Rigid Round Pillar"),
            ("2 Key", "Spawn Rigid Box Platform"),
            ("3 Key", "Cycle Material (Jello/Balloon/Foam)"),
            ("M Key", "Toggle Inner Structural Bracing"),
            ("Hold D", "Continuous Eraser Brush (Hover to delete)"),
            ("R Key", "Recenter Viewport onto Main Stage"),
            ("C + Drag", "Slicing Knife (Cut through spring meshes)"),
            ("L-Click Drag", "Grab / Move dynamic soft nodes"),
            ("M-Click Drag", "Pan / Navigate the map view")
        ]
        curr_y = panel_y + 40
        for k, desc in controls:
            self.renderer.draw_text(self.font_bold, k, ACCENT_COLOR, (panel_x + 15, curr_y))
            self.renderer.draw_text(self.font, desc, TEXT_COLOR, (panel_x + 130, curr_y))
            curr_y += 24

    def update(self):
        dt = 1.0 / FPS
        for _ in range(3): 
            self.world.update(dt / 3.0)
            bx_min, bx_max, by_min, by_max = self.world_bounds
            for p in self.world.particles:
                if p.is_static: continue
                if p.pos[0] < bx_min + p.radius:
                    p.pos[0] = bx_min + p.radius
                    vx = p.pos[0] - p.prev_pos[0]
                    p.prev_pos[0] = p.pos[0] + vx * 0.5
                elif p.pos[0] > bx_max - p.radius:
                    p.pos[0] = bx_max - p.radius
                    vx = p.pos[0] - p.prev_pos[0]
                    p.prev_pos[0] = p.pos[0] + vx * 0.5
                if p.pos[1] < by_min + p.radius:
                    p.pos[1] = by_min + p.radius
                    vy = p.pos[1] - p.prev_pos[1]
                    p.prev_pos[1] = p.pos[1] + vy * 0.5

    def render(self):
        self.renderer.clear(BACKGROUND)
        self.draw_grid()
        self.draw_world_border()
        self.world.draw(self.renderer, self.camera)
        
        if self.knife_active:
            p1 = self.camera.world_to_screen(self.knife_start)
            p2 = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, (255, 0, 0), p1, p2, 2)
            
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            world_pos = self.camera.screen_to_world(pygame.mouse.get_pos())
            
            # Continuous deletion logic if D is held down
            if keys[pygame.K_d]:
                self.process_continuous_deletion(world_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.renderer.screen = self.screen
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    elif event.key == pygame.K_m: self.spawn_structured = not self.spawn_structured
                    elif event.key == pygame.K_3: self.current_preset_idx = (self.current_preset_idx + 1) % len(self.material_presets)
                    elif event.key == pygame.K_r:
                        self.camera.zoom, self.camera.x, self.camera.y = 1.0, 0.0, 0.0
                    elif event.key == pygame.K_s: SoftBody(self.world, world_pos[0]-45, world_pos[1]-45, "square", size=90.0, preset=self.get_current_preset(), structured=self.spawn_structured)
                    elif event.key == pygame.K_t: SoftBody(self.world, world_pos[0], world_pos[1], "triangle", size=60.0, preset=self.get_current_preset(), structured=self.spawn_structured)
                    elif event.key == pygame.K_p: SoftBody(self.world, world_pos[0], world_pos[1], "pentagon", size=60.0, preset=self.get_current_preset(), structured=self.spawn_structured)
                    elif event.key == pygame.K_1: self.world.obstacles.append(Obstacle(world_pos[0], world_pos[1], "circle", r=40.0))
                    elif event.key == pygame.K_2: self.world.obstacles.append(Obstacle(world_pos[0], world_pos[1], "box", w=120.0, h=35.0))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  
                        if keys[pygame.K_c]:
                            self.knife_active = True
                            self.knife_start = world_pos
                        elif keys[pygame.K_SPACE]:
                            self.dragging, self.last_mouse = True, event.pos
                        else:
                            clicked_particle = None
                            for p in self.world.particles:
                                dx, dy = p.pos[0] - world_pos[0], p.pos[1] - world_pos[1]
                                if (dx*dx + dy*dy) < 400.0:
                                    clicked_particle = p
                                    break
                            if clicked_particle and not clicked_particle.is_static: 
                                self.selected_particle = clicked_particle
                    elif event.button == 2:
                        self.dragging, self.last_mouse = True, event.pos
                    elif event.button == 4: self.camera.zoom_in()
                    elif event.button == 5: self.camera.zoom_out()
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.knife_active:
                        world_end = self.camera.screen_to_world(event.pos)
                        sliced_springs = []
                        for s in self.world.springs:
                            if self.line_intersects(self.knife_start, world_end, s.p1.pos, s.p2.pos):
                                sliced_springs.append(s)
                        for s in sliced_springs:
                            if s in self.world.springs: self.world.springs.remove(s)
                            for sb in self.world.soft_bodies:
                                if s in sb.springs: sb.springs.remove(s)
                        self.knife_active = False
                    if event.button in (1, 2): self.selected_particle, self.dragging = None, False
                        
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx, dy = event.pos[0] - self.last_mouse[0], event.pos[1] - self.last_mouse[1]
                        self.camera.move(dx, dy)
                        self.last_mouse = event.pos
                    elif self.selected_particle:
                        world_mouse = self.camera.screen_to_world(event.pos)
                        self.selected_particle.pos = [world_mouse[0], world_mouse[1]]
                        self.selected_particle.prev_pos = [world_mouse[0], world_mouse[1]]

            self.update()
            self.render()
        pygame.quit()


