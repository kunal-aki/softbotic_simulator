import pygame


class Renderer:

    def __init__(self, screen):
        self.screen = screen


    def clear(self,color):
        self.screen.fill(color)


    def draw_line(self,color,start,end,width=1):

        pygame.draw.line(
            self.screen,
            color,
            start,
            end,
            width
        )


    def draw_circle(self,color,pos,radius):

        pygame.draw.circle(
            self.screen,
            color,
            pos,
            radius
        )


    def draw_text(self,font,text,color,pos):

        surface = font.render(
            text,
            True,
            color
        )

        self.screen.blit(surface,pos)

