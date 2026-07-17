import pygame
from config import *
from renderer import Renderer
from camera import Camera
from world import World

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE + ' v0.3 — Physics Engine')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 18)
        self.renderer = Renderer(self.screen)
        self.camera = Camera()
        self.world = World()
        self.running = True
        self.dragging = False
        self.last_mouse = (0, 0)

        # Pre-populate a standard structural pendulum setup to verify physics engine health at startup
        p1 = self.world.add_particle(300, 150, is_static=True)
        p2 = self.world.add_particle(600, 150, is_static=True)
        p3 = self.world.add_particle(450, 350, mass=2.0)
        
        self.world.add_spring(p1, p3, k=250.0, damping=2.0)
        self.world.add_spring(p2, p3, k=250.0, damping=2.0)

    def draw_grid(self):
        spacing = GRID_SIZE * self.camera.zoom
        if spacing < 10: 
            return
        ox = (self.camera.x * self.camera.zoom) % spacing
        oy = (self.camera.y * self.camera.zoom) % spacing
        x = -spacing
        while x < WIDTH + spacing:
            self.renderer.draw_line(GRID_COLOR, (x + ox, 0), (x + ox, HEIGHT))
            x += spacing
        y = -spacing
        while y < HEIGHT + spacing:
            self.renderer.draw_line(GRID_COLOR, (0, y + oy), (WIDTH, y + oy))
            y += spacing

    def draw_ui(self):
        fps = self.clock.get_fps()
        world_mouse = self.camera.screen_to_world(pygame.mouse.get_pos())
        self.renderer.draw_text(self.font, f'FPS: {fps:.1f}', TEXT_COLOR, (10, 10))
        self.renderer.draw_text(self.font, f'Zoom: {self.camera.zoom:.2f}', TEXT_COLOR, (10, 30))
        self.renderer.draw_text(self.font, f'World Mouse: ({world_mouse[0]:.1f}, {world_mouse[1]:.1f})', TEXT_COLOR, (10, 50))
        self.renderer.draw_text(self.font, f'Particles Total: {len(self.world.particles)}', TEXT_COLOR, (10, 70))
        self.renderer.draw_text(self.font, 'L-Click: Add Mass Node | Shift+L-Click: Add Anchor | M-Drag: Pan Canvas', TEXT_COLOR, (10, HEIGHT - 30))

    def update(self):
        dt = 1.0 / FPS
        self.world.update(dt)

    def render(self):
        self.renderer.clear(BACKGROUND)
        self.draw_grid()
        self.world.draw(self.renderer, self.camera)
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left Click
                        world_pos = self.camera.screen_to_world(event.pos)
                        keys = pygame.key.get_pressed()
                        is_static = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                        self.world.add_particle(world_pos[0], world_pos[1], is_static=is_static)
                        
                    elif event.button == 2:  # Middle Click Pan
                        self.dragging = True
                        self.last_mouse = event.pos
                    elif event.button == 4:  # Zoom In
                        self.camera.zoom_in()
                    elif event.button == 5:  # Zoom Out
                        self.camera.zoom_out()
                        
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                    self.dragging = False
                    
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    dx = event.pos[0] - self.last_mouse[0]
                    dy = event.pos[1] - self.last_mouse[1]
                    self.camera.move(dx, dy)
                    self.last_mouse = event.pos

            self.update()
            self.render()

        pygame.quit()


