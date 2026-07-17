import pygame

from engine.config import *
from engine.renderer import Renderer
from engine.camera import Camera

from objects.world import World



class App:


    def __init__(self):

        pygame.init()


        self.screen=pygame.display.set_mode(
            (WIDTH,HEIGHT)
        )


        pygame.display.set_caption(
            TITLE+" v0.3"
        )


        self.clock=pygame.time.Clock()


        self.font=pygame.font.SysFont(
            "arial",
            18
        )


        self.renderer=Renderer(
            self.screen
        )


        self.camera=Camera()


        self.world=World()


        # test particle

        self.world.add_particle(
            (700,200)
        )


        self.running=True

        self.dragging=False

        self.last_mouse=(0,0)



    def draw_grid(self):

        spacing=GRID_SIZE*self.camera.zoom


        if spacing<10:
            return


        ox=(self.camera.x*self.camera.zoom)%spacing

        oy=(self.camera.y*self.camera.zoom)%spacing


        x=-spacing

        while x<WIDTH+spacing:

            self.renderer.draw_line(
                GRID_COLOR,
                (x+ox,0),
                (x+ox,HEIGHT)
            )

            x+=spacing



        y=-spacing

        while y<HEIGHT+spacing:

            self.renderer.draw_line(
                GRID_COLOR,
                (0,y+oy),
                (WIDTH,y+oy)
            )

            y+=spacing



    def draw_ui(self):

        fps=self.clock.get_fps()


        self.renderer.draw_text(
            self.font,
            f"FPS: {fps:.1f}",
            TEXT_COLOR,
            (10,10)
        )


        self.renderer.draw_text(
            self.font,
            "BioSim v0.3 Physics",
            TEXT_COLOR,
            (10,30)
        )



    def render(self):

        self.renderer.clear(
            BACKGROUND
        )


        self.draw_grid()


        self.world.draw(
            self.renderer,
            self.camera
        )


        self.draw_ui()


        pygame.display.flip()



    def run(self):

        while self.running:


            dt=self.clock.tick(FPS)/1000



            for event in pygame.event.get():


                if event.type==pygame.QUIT:

                    self.running=False



                elif event.type==pygame.MOUSEBUTTONDOWN:


                    if event.button==2:

                        self.dragging=True

                        self.last_mouse=event.pos



                    elif event.button==4:

                        self.camera.zoom_in()



                    elif event.button==5:

                        self.camera.zoom_out()



                elif event.type==pygame.MOUSEBUTTONUP:


                    if event.button==2:

                        self.dragging=False



                elif event.type==pygame.MOUSEMOTION:


                    if self.dragging:

                        dx=event.pos[0]-self.last_mouse[0]

                        dy=event.pos[1]-self.last_mouse[1]


                        self.camera.move(
                            dx,
                            dy
                        )


                        self.last_mouse=event.pos



            self.world.update(
                dt
            )


            self.render()



        pygame.quit()

