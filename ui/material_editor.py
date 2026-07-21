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
            "Rectangle",
            "Circle"
        ]

        self.selected = 0


    def draw_menu(self, screen, font):

        pygame.draw.rect(
            screen,
            PANEL,
            (0, 0, WIDTH, MENU_HEIGHT)
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (0, MENU_HEIGHT),
            (WIDTH, MENU_HEIGHT)
        )

        labels = [
            "File",
            "Edit",
            "View",
            "CAD",
            "Simulation",
            "Analysis",
            "Help"
        ]

        x = 10

        for label in labels:

            text = font.render(
                label,
                True,
                TEXT_COLOR
            )

            screen.blit(text, (x, 6))

            x += 80


    def draw_toolbar(self, screen, font):

        pygame.draw.rect(
            screen,
            PANEL,
            (0,
             MENU_HEIGHT,
             TOOLBAR_WIDTH,
             HEIGHT)
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (TOOLBAR_WIDTH, 0),
            (TOOLBAR_WIDTH, HEIGHT)
        )

        y = MENU_HEIGHT + 12

        for i, tool in enumerate(self.tools):

            rect = pygame.Rect(
                8,
                y,
                TOOLBAR_WIDTH - 16,
                40
            )

            color = PANEL_LIGHT

            if i == self.selected:
                color = (70, 120, 180)

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=6
            )

            txt = font.render(
                tool[0],
                True,
                (255,255,255)
            )

            screen.blit(
                txt,
                (
                    rect.centerx - txt.get_width()/2,
                    rect.centery - txt.get_height()/2
                )
            )

            y += 50


    def draw_properties(self, screen, font):

        x = WIDTH - PROPERTY_WIDTH

        pygame.draw.rect(
            screen,
            PANEL,
            (
                x,
                MENU_HEIGHT,
                PROPERTY_WIDTH,
                HEIGHT
            )
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (x,0),
            (x,HEIGHT)
        )

        title = font.render(
            "Properties",
            True,
            TEXT_COLOR
        )

        screen.blit(
            title,
            (
                x + 15,
                MENU_HEIGHT + 10
            )
        )

        rows = [
            "Name:",
            "Material:",
            "Mass:",
            "Density:",
            "Stiffness:",
            "Pressure:",
            "Selected:"
        ]

        y = MENU_HEIGHT + 50

        for row in rows:

            text = font.render(
                row,
                True,
                TEXT_COLOR
            )

            screen.blit(
                text,
                (
                    x + 15,
                    y
                )
            )

            y += 30


    def draw_status(self, screen, font):

        pygame.draw.rect(
            screen,
            PANEL,
            (
                0,
                HEIGHT - STATUS_HEIGHT,
                WIDTH,
                STATUS_HEIGHT
            )
        )

        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (0, HEIGHT - STATUS_HEIGHT),
            (WIDTH, HEIGHT - STATUS_HEIGHT)
        )


    def draw(self, screen, font):

        self.draw_menu(
            screen,
            font
        )

        self.draw_toolbar(
            screen,
            font
        )

        self.draw_properties(
            screen,
            font
        )

        self.draw_status(
            screen,
            font
        )


