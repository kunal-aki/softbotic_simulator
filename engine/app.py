import pygame

from engine.config import *
from engine.renderer import Renderer
from engine.camera import Camera
from engine.scene import Scene
from engine.selection import SelectionManager
from engine.history import History
from materials.library import MaterialLibrary
from ui.manager import UIManager


class App:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 16)

        self.renderer = Renderer(self.screen)
        self.camera = Camera()

        self.scene = Scene()
        self.selection = SelectionManager()
        self.history = History()
        self.materials = MaterialLibrary()
        self.ui = UIManager()

        self.running = True
        self.dragging = False
        self.last_mouse = (0, 0)

        self.current_tool = "Select"
        self.selected_object = None
        self.hover_object = None
        self.status_text = "Ready"

    def viewport_rect(self):
        return pygame.Rect(
            VIEWPORT_X,
            VIEWPORT_Y,
            VIEWPORT_WIDTH,
            VIEWPORT_HEIGHT
        )

    def screen_to_world(self, screen_pos):
        """Convert screen pixel coordinates into world coordinates."""
        cam_x = getattr(self.camera, 'x', getattr(self.camera, 'offset_x', 0.0))
        cam_y = getattr(self.camera, 'y', getattr(self.camera, 'offset_y', 0.0))

        rel_x = screen_pos[0] - VIEWPORT_X
        rel_y = screen_pos[1] - VIEWPORT_Y

        world_x = (rel_x / self.camera.zoom) - cam_x
        world_y = (rel_y / self.camera.zoom) - cam_y
        return (world_x, world_y)

    def draw_grid(self):
        viewport = self.viewport_rect()
        spacing = GRID_SIZE * self.camera.zoom

        if spacing < 8:
            return

        cam_x = getattr(self.camera, 'x', getattr(self.camera, 'offset_x', 0.0))
        cam_y = getattr(self.camera, 'y', getattr(self.camera, 'offset_y', 0.0))

        ox = (cam_x * self.camera.zoom) % spacing
        oy = (cam_y * self.camera.zoom) % spacing

        x = viewport.left - spacing
        while x < viewport.right + spacing:
            start_p = (int(x + ox), int(viewport.top))
            end_p = (int(x + ox), int(viewport.bottom))
            self.renderer.draw_line(GRID_COLOR, start_p, end_p)
            x += spacing

        y = viewport.top - spacing
        while y < viewport.bottom + spacing:
            start_p = (int(viewport.left), int(y + oy))
            end_p = (int(viewport.right), int(y + oy))
            self.renderer.draw_line(GRID_COLOR, start_p, end_p)
            y += spacing

    def set_tool(self, tool_name):
        """Update active tool and synchronize with UI manager."""
        self.current_tool = tool_name
        self.ui.select_tool_by_name(tool_name)
        self.status_text = f"Tool: {tool_name}"

    def spawn_object_at(self, world_pos):
        """CAD Tool creation factory."""
        wx, wy = world_pos
        obj = None

        if self.current_tool == "Particle":
            if hasattr(self.scene, 'add_particle'):
                obj = self.scene.add_particle(wx, wy)
            else:
                obj = self.scene.add_object("particle", x=wx, y=wy)
            self.status_text = f"Created Particle at ({wx:.1f}, {wy:.1f})"

        elif self.current_tool in ["Rect", "Circle"]:
            shape = "square" if self.current_tool == "Rect" else "circle"
            if hasattr(self.scene, 'create_soft_body'):
                obj = self.scene.create_soft_body(wx, wy, shape=shape)
            else:
                obj = self.scene.add_object(shape, x=wx, y=wy)
            self.status_text = f"Created {self.current_tool} Soft Body at ({wx:.1f}, {wy:.1f})"

        elif self.current_tool == "Spring":
            self.status_text = "Click second point to connect Spring"
            return

        if obj is not None:
            self.selected_object = obj
            if hasattr(self.selection, 'set_selected'):
                self.selection.set_selected(obj)
            if hasattr(self.history, 'record_action'):
                self.history.record_action("CREATE", obj)

    def update(self, dt):
        self.scene.update(dt)

    def render(self):
        self.renderer.clear(BACKGROUND)
        viewport = self.viewport_rect()

        self.renderer.set_clip(viewport)
        self.draw_grid()

        if hasattr(self.scene, 'draw'):
            self.scene.draw(self.renderer, self.camera)
        elif hasattr(self.scene, 'render'):
            self.scene.render(self.renderer, self.camera)

        if self.selected_object and hasattr(self.renderer, 'draw_selection'):
            self.renderer.draw_selection(self.selected_object, self.camera)

        self.renderer.clear_clip()

        self.ui.draw(self.screen, self.font, selected_object=self.selected_object, status_text=self.status_text)
        self.renderer.draw_viewport_border(viewport)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_q:
                    self.set_tool("Select")
                elif event.key == pygame.K_w:
                    self.set_tool("Move")
                elif event.key == pygame.K_e:
                    self.set_tool("Rotate")
                elif event.key == pygame.K_r:
                    self.set_tool("Scale")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # 1. UI Toolbar Clicks
                clicked_tool = self.ui.handle_click(mouse_pos)
                if clicked_tool:
                    self.set_tool(clicked_tool)
                    continue

                # 2. Viewport Mouse Interactions
                viewport = self.viewport_rect()
                if viewport.collidepoint(mouse_pos):
                    world_pos = self.screen_to_world(mouse_pos)

                    if event.button == 1:  # Left Click
                        if self.current_tool == "Select":
                            if hasattr(self.scene, 'pick_object'):
                                self.selected_object = self.scene.pick_object(world_pos)
                                if hasattr(self.selection, 'set_selected'):
                                    self.selection.set_selected(self.selected_object)
                                if self.selected_object:
                                    self.status_text = f"Selected: {self.selected_object}"
                                else:
                                    self.status_text = "Cleared Selection"
                        else:
                            self.spawn_object_at(world_pos)

                    elif event.button == 2:  # Middle Mouse Pan
                        self.dragging = True
                        self.last_mouse = mouse_pos

                    elif event.button == 4:  # Scroll Up Zoom
                        if hasattr(self.camera, 'zoom_in'):
                            self.camera.zoom_in()
                        else:
                            self.camera.zoom *= 1.1

                    elif event.button == 5:  # Scroll Down Zoom
                        if hasattr(self.camera, 'zoom_out'):
                            self.camera.zoom_out()
                        else:
                            self.camera.zoom /= 1.1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_mouse[0]
                    dy = event.pos[1] - self.last_mouse[1]

                    if hasattr(self.camera, 'move'):
                        self.camera.move(dx, dy)
                    elif hasattr(self.camera, 'pan'):
                        self.camera.pan(dx, dy)
                    else:
                        if hasattr(self.camera, 'x'):
                            self.camera.x += dx
                            self.camera.y += dy
                        elif hasattr(self.camera, 'offset_x'):
                            self.camera.offset_x += dx
                            self.camera.offset_y += dy

                    self.last_mouse = event.pos

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()


