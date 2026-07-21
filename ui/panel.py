import pygame


class Panel:

    def __init__(
        self,
        x,
        y,
        w,
        h,
        title
    ):

        self.rect=pygame.Rect(
            x,
            y,
            w,
            h
        )

        self.title=title

        self.visible=True


    def draw(self,screen,font):

        if not self.visible:

            return


        pygame.draw.rect(
            screen,
            (40,40,45),
            self.rect
        )

        pygame.draw.rect(
            screen,
            (80,80,90),
            self.rect,
            1
        )

        text=font.render(
            self.title,
            True,
            (230,230,230)
        )

        screen.blit(
            text,
            (
                self.rect.x+8,
                self.rect.y+6
            )
        )

