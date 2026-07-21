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



        self.screen = pygame.display.set_mode(
            (
                WIDTH,
                HEIGHT
            )
        )



        pygame.display.set_caption(
            TITLE + " v2.0"
        )



        self.clock = pygame.time.Clock()



        self.font = pygame.font.SysFont(
            "arial",
            18
        )



        self.renderer = Renderer(
            self.screen
        )



        self.camera = Camera()



        # v2.0 systems


        self.scene = Scene()


        self.selection = SelectionManager()


        self.history = History()


        self.materials = MaterialLibrary()



        self.ui = UIManager()



        self.running = True



        self.dragging=False

        self.last_mouse=(0,0)



    # -------------------------
    # VIEWPORT
    # -------------------------


    def viewport_rect(self):


        return pygame.Rect(

            TOOLBAR_WIDTH,

            MENU_HEIGHT,

            WIDTH
            -
            TOOLBAR_WIDTH
            -
            PROPERTY_WIDTH,

            HEIGHT
            -
            MENU_HEIGHT
            -
            STATUS_HEIGHT

        )



    def draw_grid(self):


        viewport=self.viewport_rect()



        spacing = GRID_SIZE * self.camera.zoom



        if spacing < 8:

            return



        offset_x = (
            self.camera.x
            *
            self.camera.zoom
        ) % spacing



        offset_y = (
            self.camera.y
            *
            self.camera.zoom
        ) % spacing



        x = viewport.left-spacing



        while x < viewport.right+spacing:


            self.renderer.draw_line(

                GRID_COLOR,

                (
                    x+offset_x,
                    viewport.top
                ),

                (
                    x+offset_x,
                    viewport.bottom
                )

            )


            x += spacing




        y = viewport.top-spacing



        while y < viewport.bottom+spacing:


            self.renderer.draw_line(

                GRID_COLOR,

                (
                    viewport.left,
                    y+offset_y
                ),

                (
                    viewport.right,
                    y+offset_y
                )

            )


            y += spacing





    # -------------------------
    # UI INFORMATION
    # -------------------------


    def draw_viewport_info(self):


        mouse = pygame.mouse.get_pos()


        world = self.camera.screen_to_world(
            mouse
        )


        self.renderer.draw_text(

            self.font,

            f"FPS: {self.clock.get_fps():.1f}",

            TEXT_COLOR,

            (
                TOOLBAR_WIDTH+10,
                MENU_HEIGHT+10
            )

        )



        self.renderer.draw_text(

            self.font,

            f"Zoom: {self.camera.zoom:.2f}",

            TEXT_COLOR,

            (
                TOOLBAR_WIDTH+10,
                MENU_HEIGHT+35
            )

        )



        self.renderer.draw_text(

            self.font,

            f"World: ({world[0]:.1f}, {world[1]:.1f})",

            TEXT_COLOR,

            (
                TOOLBAR_WIDTH+10,
                MENU_HEIGHT+60
            )

        )





    # -------------------------
    # UPDATE
    # -------------------------


    def update(self,dt):


        self.scene.update(
            dt
        )




    # -------------------------
    # DRAW
    # -------------------------


    def render(self):


        self.renderer.clear(
            BACKGROUND
        )



        # viewport

        self.draw_grid()



        self.scene.draw(

            self.renderer,

            self.camera

        )



        self.draw_viewport_info()



        # UI

        self.ui.draw(

            self.screen,

            self.font

        )



        self.renderer.draw_viewport_border(

            self.viewport_rect()

        )



        pygame.display.flip()




    # -------------------------
    # EVENTS
    # -------------------------


    def handle_events(self):


        for event in pygame.event.get():



            if event.type == pygame.QUIT:


                self.running=False




            elif event.type == pygame.MOUSEBUTTONDOWN:


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


                    dx = (
                        event.pos[0]
                        -
                        self.last_mouse[0]
                    )


                    dy = (
                        event.pos[1]
                        -
                        self.last_mouse[1]
                    )


                    self.camera.move(
                        dx,
                        dy
                    )


                    self.last_mouse=event.pos





    # -------------------------
    # MAIN LOOP
    # -------------------------


    def run(self):


        while self.running:


            dt = (
                self.clock.tick(FPS)
                /
                1000
            )



            self.handle_events()



            self.update(
                dt
            )



            self.render()



        pygame.quit()


