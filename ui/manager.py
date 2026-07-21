import pygame
from engine.config import *


class UIManager:

    def __init__(self):
        self.tools = [
            "Select",
            "Move",
            "Rotate",
            "Scale",
            "Particle",
            "Spring",
            "Rect",
            "Circle"
        ]
        self.selected = 0

    def get_tool_rect(self, index):
        """Calculate exact bounding box for a toolbar button."""
        y = MENU_HEIGHT + 10 + index * (38 + 6)
        button_width = TOOLBAR_WIDTH - 16
        return pygame.Rect(8, y, button_width, 38)

    def handle_click(self, mouse_pos):
        """Process click on toolbar. Returns selected tool name if clicked, else None."""
        if mouse_pos[0] < TOOLBAR_WIDTH and MENU_HEIGHT <= mouse_pos[1] < MENU_HEIGHT + VIEWPORT_HEIGHT:
            for i in range(len(self.tools)):
                rect = self.get_tool_rect(i)
                if rect.collidepoint(mouse_pos):
                    self.selected = i
                    return self.tools[i]
        return None

    def select_tool_by_name(self, name):
        """Sync tool selection index from name (e.g. keyboard shortcuts)."""
        if name in self.tools:
            self.selected = self.tools.index(name)

    def draw(self, screen, font, selected_object=None, status_text="Ready"):
        self.draw_menu(screen, font)
        self.draw_toolbar(screen, font)
        self.draw_properties(screen, font, selected_object)
        self.draw_status(screen, font, status_text)

    def draw_menu(self, screen, font):
        pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, MENU_HEIGHT))
        pygame.draw.line(screen, PANEL_BORDER, (0, MENU_HEIGHT - 1), (WIDTH, MENU_HEIGHT - 1), 1)

        labels = ["File", "Edit", "View", "CAD", "Simulation", "Analysis", "Help"]
        x = 15
        for label in labels:
            text = font.render(label, True, TEXT_COLOR)
            # Centered vertically in the expanded 42px MENU_HEIGHT
            text_y = (MENU_HEIGHT - text.get_height()) // 2
            screen.blit(text, (x, text_y))
            x += 85

    def draw_toolbar(self, screen, font):
        pygame.draw.rect(screen, PANEL, (0, MENU_HEIGHT, TOOLBAR_WIDTH, VIEWPORT_HEIGHT))
        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (TOOLBAR_WIDTH - 1, MENU_HEIGHT),
            (TOOLBAR_WIDTH - 1, MENU_HEIGHT + VIEWPORT_HEIGHT)
        )

        button_width = TOOLBAR_WIDTH - 16

        for i, tool in enumerate(self.tools):
            rect = self.get_tool_rect(i)
            color = PANEL_LIGHT
            if i == self.selected:
                color = (70, 120, 180)

            pygame.draw.rect(screen, color, rect, border_radius=5)

            text = font.render(tool, True, TEXT_COLOR)
            max_width = button_width - 8
            if text.get_width() > max_width:
                scale_ratio = max_width / text.get_width()
                new_size = (int(text.get_width() * scale_ratio), int(text.get_height() * scale_ratio))
                text = pygame.transform.smoothscale(text, new_size)

            screen.blit(
                text,
                (
                    rect.centerx - text.get_width() // 2,
                    rect.centery - text.get_height() // 2
                )
            )

    def draw_properties(self, screen, font, selected_object=None):
        x = WIDTH - PROPERTY_WIDTH
        pygame.draw.rect(screen, PANEL, (x, MENU_HEIGHT, PROPERTY_WIDTH, VIEWPORT_HEIGHT))
        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (x, MENU_HEIGHT),
            (x, MENU_HEIGHT + VIEWPORT_HEIGHT)
        )

        title = font.render("Properties", True, TEXT_COLOR)
        screen.blit(title, (x + 15, MENU_HEIGHT + 12))

        obj_name = str(selected_object) if selected_object else "None Selected"
        items = [
            f"Target: {obj_name}",
            "Position: --",
            "Rotation: 0.0°",
            "Scale: 1.0",
            "Material: Standard",
            "Density: 1.0",
            "Stiffness: 100",
            "Pressure: 1.0"
        ]

        y = MENU_HEIGHT + 48
        for item in items:
            text = font.render(item, True, TEXT_COLOR)
            screen.blit(text, (x + 15, y))
            y += 32

    def draw_status(self, screen, font, status_text="Ready"):
        pygame.draw.rect(screen, PANEL, (0, HEIGHT - STATUS_HEIGHT, WIDTH, STATUS_HEIGHT))
        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (0, HEIGHT - STATUS_HEIGHT),
            (WIDTH, HEIGHT - STATUS_HEIGHT)
        )

        text = font.render(f"BioSim v2.0.3 | Status: {status_text}", True, TEXT_COLOR)
        text_y = (HEIGHT - STATUS_HEIGHT) + (STATUS_HEIGHT - text.get_height()) // 2
        screen.blit(text, (12, text_y))


