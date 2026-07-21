class Camera:


    def __init__(self):

        self.offset_x = 0
        self.offset_y = 0

        self.zoom = 1.0

        self.min_zoom = 0.25
        self.max_zoom = 5.0



    # -------------------------
    # WORLD -> SCREEN
    # -------------------------

    def world_to_screen(self,pos):

        x = (
            pos[0] + self.offset_x
        ) * self.zoom


        y = (
            pos[1] + self.offset_y
        ) * self.zoom


        return (
            int(x),
            int(y)
        )



    # -------------------------
    # SCREEN -> WORLD
    # -------------------------

    def screen_to_world(self,pos):

        x = (
            pos[0] / self.zoom
        ) - self.offset_x


        y = (
            pos[1] / self.zoom
        ) - self.offset_y


        return (
            x,
            y
        )



    # -------------------------
    # PAN CAMERA
    # -------------------------

    def pan(self,dx,dy):

        self.offset_x += (
            dx / self.zoom
        )


        self.offset_y += (
            dy / self.zoom
        )



    # Compatibility

    def move(self,dx,dy):

        self.pan(
            dx,
            dy
        )



    # -------------------------
    # ZOOM
    # -------------------------

    def zoom_in(self):

        self.zoom = min(
            self.max_zoom,
            self.zoom * 1.1
        )



    def zoom_out(self):

        self.zoom = max(
            self.min_zoom,
            self.zoom / 1.1
        )

