import pygame


class MenuBar:

    def __init__(self):

        self.height=28

        self.items=[

            "File",

            "Edit",

            "View",

            "CAD",

            "Simulation",

            "Analysis",

            "Help"

        ]


    def draw(self,screen,font):

        pygame.draw.rect(

            screen,

            (35,35,38),

            (0,0,1400,self.height)

        )


        x=10

        for item in self.items:

            text=font.render(

                item,

                True,

                (240,240,240)

            )

            screen.blit(

                text,

                (x,5)

            )

            x+=80

