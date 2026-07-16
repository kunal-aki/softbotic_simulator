import pygame

from engine.config import *
from engine.renderer import Renderer
from engine.camera import Camera



class App:


    def __init__(self):

        pygame.init()


        self.screen=pygame.display.set_mode(
            (WIDTH,HEIGHT)
        )


        pygame.display.set_caption(
            TITLE
        )


        self.clock=pygame.time.Clock()


        self.font=pygame.font.SysFont(
            "arial",
            20
        )


        self.renderer=Renderer(
            self.screen
        )


        self.camera=Camera()


        self.running=True



    def update(self):

        pass



    def draw_grid(self):

        for x in range(
            0,
            WIDTH,
            GRID_SIZE
        ):

            self.renderer.draw_line(
                GRID_COLOR,
                (x,0),
                (x,HEIGHT)
            )


        for y in range(
            0,
            HEIGHT,
            GRID_SIZE
        ):

            self.renderer.draw_line(
                GRID_COLOR,
                (0,y),
                (WIDTH,y)
            )


    def render(self):

        self.renderer.clear(
            BACKGROUND
        )


        self.draw_grid()


        self.renderer.draw_text(
            self.font,
            "BioSim v0.1",
            TEXT_COLOR,
            (20,20)
        )


        pygame.display.flip()



    def run(self):

        while self.running:


            self.clock.tick(FPS)


            for event in pygame.event.get():

                if event.type==pygame.QUIT:

                    self.running=False



            self.update()

            self.render()



        pygame.quit()

