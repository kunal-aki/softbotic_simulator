"""
BioSim v2.0 - Core Application Logic
Orchestrates event loops, CAD interactive creation tools, viewport interaction, and solvers.
"""

import pygame

from engine.config import (
    WIDTH, HEIGHT, TITLE, FPS, VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, COLOR_VIEWPORT_BG
)
from engine.renderer import Renderer
from engine.camera import Camera
from engine.scene import Scene, Particle, SoftBodyMesh
from ui.manager import UIManager


class App:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 13)

        self.renderer = Renderer(self.screen)
        self.camera = Camera()

        self.scene = Scene()
        self.ui = UIManager()

        self.running = True
        self.dragging_camera = False
        self.dragging_object = False
        self.creating_rectangle = False
        self.rect_start_world = None

        self.last_mouse = (0, 0)
        self.selected_object = None
        self.spring_first_particle = None
        self.status_text = "BioSim v2.0 Workspace Ready"

    def viewport_rect(self):
        return pygame.Rect(VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

    def screen_to_world(self, screen_pos):
        """Accurately convert viewport pixel positions into world coordinates."""
        rel_x = screen_pos[0] - VIEWPORT_X
        rel_y = screen_pos[1] - VIEWPORT_Y

        world_x = (rel_x / self.camera.zoom) - self.camera.x
        world_y = (rel_y / self.camera.zoom) - self.camera.y
        return (world_x, world_y)

    def set_tool_by_name(self, name):
        if self.ui.set_active_tool_by_name(name):
            self.spring_first_particle = None
            self.status_text = f"Tool Selected: {name}"

    def update(self, dt):
        self.scene.update(dt)

    def render(self):
        self.renderer.clear((24, 26, 30))
        viewport = self.viewport_rect()

        # Render Viewport Contents
        self.renderer.set_clip(viewport)
        self.renderer.draw_rect(COLOR_VIEWPORT_BG, viewport)
        self.renderer.draw_grid_and_axes(self.camera)

        self.scene.draw(self.renderer, self.camera)

        if self.selected_object:
            self.renderer.draw_selection_gizmo(self.selected_object, self.camera)

        # Dynamic Rectangle Creation Drag Preview
        if self.creating_rectangle and self.rect_start_world:
            curr_world = self.screen_to_world(pygame.mouse.get_pos())
            sx1 = int((self.rect_start_world[0] + self.camera.x) * self.camera.zoom) + VIEWPORT_X
            sy1 = int((self.rect_start_world[1] + self.camera.y) * self.camera.zoom) + VIEWPORT_Y
            sx2 = int((curr_world[0] + self.camera.x) * self.camera.zoom) + VIEWPORT_X
            sy2 = int((curr_world[1] + self.camera.y) * self.camera.zoom) + VIEWPORT_Y

            rect_w = abs(sx2 - sx1)
            rect_h = abs(sy2 - sy1)
            rx = min(sx1, sx2)
            ry = min(sy1, sy2)
            self.renderer.draw_rect((0, 122, 204), (rx, ry, rect_w, rect_h), width=1)

        self.renderer.clear_clip()

        # Render CAD UI
        self.ui.draw(
            self.screen,
            self.font,
            self.camera,
            self.selected_object,
            self.status_text,
            self.scene.paused,
            self.scene,
            pygame.mouse.get_pos()
        )
        self.renderer.draw_viewport_border()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    self.scene.paused = not self.scene.paused
                    self.status_text = "Simulation Running" if not self.scene.paused else "Simulation Paused"

                elif event.key in [pygame.K_DELETE, pygame.K_BACKSPACE]:
                    if self.selected_object:
                        self.scene.remove_object(self.selected_object)
                        self.selected_object = None
                        self.status_text = "Deleted Selected Object"

                # Functional Milestone 2 Hotkeys
                elif event.key == pygame.K_q:
                    self.set_tool_by_name("Select")
                elif event.key == pygame.K_w:
                    self.set_tool_by_name("Move")
                elif event.key == pygame.K_e:
                    self.set_tool_by_name("Rotate")
                elif event.key == pygame.K_r:
                    self.set_tool_by_name("Scale")
                elif event.key == pygame.K_p:
                    self.set_tool_by_name("Particle")
                elif event.key == pygame.K_s:
                    self.set_tool_by_name("Spring")
                elif event.key == pygame.K_b:
                    self.set_tool_by_name("Rectangle Mesh")
                elif event.key == pygame.K_c:
                    self.set_tool_by_name("Circle Mesh")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # UI Click Intercept
                ui_action = self.ui.handle_click(mouse_pos, self.scene, self)
                if ui_action:
                    if ui_action not in ["menu", "menu_action", "material_assigned"]:
                        self.set_tool_by_name(ui_action)
                    continue

                viewport = self.viewport_rect()
                if viewport.collidepoint(mouse_pos):
                    world_pos = self.screen_to_world(mouse_pos)
                    active_tool = self.ui.get_active_tool_name()

                    if event.button == 1:  # Left Click
                        if active_tool == "Select":
                            self.selected_object = self.scene.pick_object(world_pos)
                            self.status_text = f"Selected: {self.selected_object.name}" if self.selected_object else "Cleared Selection"

                        elif active_tool in ["Move", "Rotate", "Scale"]:
                            target = self.scene.pick_object(world_pos)
                            if target:
                                self.selected_object = target
                            self.dragging_object = True
                            self.last_mouse = mouse_pos

                        elif active_tool == "Particle":
                            p = self.scene.add_particle(world_pos[0], world_pos[1])
                            self.selected_object = p
                            self.status_text = f"Created Particle at ({world_pos[0]:.1f}, {world_pos[1]:.1f})"

                        elif active_tool == "Circle Mesh":
                            body = self.scene.add_soft_body(world_pos[0], world_pos[1], shape_type="circle", width=80.0)
                            self.selected_object = body
                            self.status_text = "Created Soft-Body Circle Mesh"

                        elif active_tool == "Rectangle Mesh":
                            self.creating_rectangle = True
                            self.rect_start_world = world_pos

                        elif active_tool == "Spring":
                            p_target = self.scene.pick_particle(world_pos)
                            if p_target:
                                if not self.spring_first_particle:
                                    self.spring_first_particle = p_target
                                    self.status_text = "Spring: First Particle Selected. Click 2nd Node."
                                else:
                                    if p_target != self.spring_first_particle:
                                        self.scene.add_spring(self.spring_first_particle, p_target)
                                        self.status_text = "Connected Spring Constraint!"
                                    self.spring_first_particle = None

                    elif event.button == 2:  # Middle Mouse Pan
                        self.dragging_camera = True
                        self.last_mouse = mouse_pos

                    elif event.button == 4:  # Scroll Up Zoom In
                        self.camera.zoom_at(1.1, mouse_pos[0], mouse_pos[1], VIEWPORT_X, VIEWPORT_Y)

                    elif event.button == 5:  # Scroll Down Zoom Out
                        self.camera.zoom_at(1.0 / 1.1, mouse_pos[0], mouse_pos[1], VIEWPORT_X, VIEWPORT_Y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.creating_rectangle and self.rect_start_world:
                        curr_world = self.screen_to_world(event.pos)
                        w = abs(curr_world[0] - self.rect_start_world[0])
                        h = abs(curr_world[1] - self.rect_start_world[1])

                        if w > 10 and h > 10:
                            cx = (self.rect_start_world[0] + curr_world[0]) / 2.0
                            cy = (self.rect_start_world[1] + curr_world[1]) / 2.0
                            body = self.scene.add_soft_body(cx, cy, shape_type="rect", width=w, height=h)
                            self.selected_object = body
                            self.status_text = f"Created Rect Mesh ({w:.0f}x{h:.0f})"

                        self.creating_rectangle = False
                        self.rect_start_world = None

                    self.dragging_object = False

                elif event.button == 2:
                    self.dragging_camera = False

            elif event.type == pygame.MOUSEMOTION:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]
                world_pos = self.screen_to_world(event.pos)

                if self.dragging_object and self.selected_object:
                    active_tool = self.ui.get_active_tool_name()

                    if active_tool == "Move":
                        if isinstance(self.selected_object, Particle):
                            self.selected_object.x = world_pos[0]
                            self.selected_object.y = world_pos[1]
                            self.selected_object.old_x = world_pos[0]
                            self.selected_object.old_y = world_pos[1]
                        elif isinstance(self.selected_object, SoftBodyMesh):
                            shift_x = dx / self.camera.zoom
                            shift_y = dy / self.camera.zoom
                            self.selected_object.x += shift_x
                            self.selected_object.y += shift_y
                            for p in self.selected_object.particles:
                                p.x += shift_x
                                p.y += shift_y
                                p.old_x = p.x
                                p.old_y = p.y

                    elif active_tool == "Rotate":
                        if isinstance(self.selected_object, SoftBodyMesh):
                            self.selected_object.rotate(dx * 0.02)

                    elif active_tool == "Scale":
                        if isinstance(self.selected_object, SoftBodyMesh):
                            factor = 1.0 + (dx * 0.01)
                            self.selected_object.apply_scale(factor)

                    self.last_mouse = event.pos

                elif self.dragging_camera:
                    self.camera.move(dx, dy)
                    self.last_mouse = event.pos

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()


